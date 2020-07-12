import sqlite3
import time
from pathlib import Path


class DB():
    def __init__(self):
        self.dbpath = str(Path.home()) + "/paperclip.db"
        self.connect()
        
    def connect(self):
            self.conn = sqlite3.connect(self.dbpath)
            self.c = self.conn.cursor()

    
    
    def setupDB(self):
        """
        setupDB makes sure the tables exist in the DB. 
        if not creates them.
        """
        
        r = self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in r.fetchall()]
        
        if "paperclip_config" not in tables:
            self.c.execute(""" CREATE TABLE paperclip_config (
                                                    cloudtype text 
                                                    )
                                                           
                            """)
            self.c.execute("INSERT INTO paperclip_config (cloudtype) VALUES ('notset') ")
            self.conn.commit()
    
        
        
        
        if "paperclip_files" not in tables:
            self.c.execute(""" CREATE TABLE paperclip_files (
                                                    filekey text ,
                                                    filename text,
                                                    filesize integer,
                                                    abspath text,
                                                    dirpath text,
                                                    objectname text,
                                                    projectname text,
                                                    projectkey text ,
                                                    state text)
                                                           
                            """)
            self.conn.commit()
        if "paperclip_projects" not in tables:
            self.c.execute(""" CREATE TABLE paperclip_projects (
                                                    projectkey text ,
                                                    projectname text,
                                                    dirpath text,
                                                    zippath text,
                                                    state text)
                                                           
                            """)
            self.conn.commit()
    
    
    
    def get_mother_config(self):
        # get config and process it right here 
        config = {}
        config_from_db = self.c.execute("SELECT * from paperclip_config").fetchall()
        config["cloudtype"] = config_from_db[0][0]
        return config
        
    def set_mother_config(self,key,value):
        # set mother config 
        self.c.execute(f"UPDATE paperclip_config SET {key}='{value}' WHERE 1 ")
        self.conn.commit()
        
    
    
    """
    Files and projects DB Tools
    """
    def check_existance(self,record,col,table):
        """
        check_existance is used in different places for checking if a row exists in a table.
        @params:
            record: the value of a record for which we're searching the DB
            col:    the colomn to select from table
            table:  the table to select from
        """
        records =  self.c.execute(f"SELECT {col} from {table}").fetchall()
        if record in [r[0] for r in records]:
            return True
        else:
            return False



    def create_project(self,project_name,project_dir,projectkey):
        if not self.check_existance(project_dir,"dirpath","paperclip_projects"):
            self.c.execute(f"""INSERT INTO paperclip_projects (projectkey,projectname,dirpath,zippath,state) 
                               VALUES (\"{projectkey}\", \"{project_name}\","{project_dir}","", \"only_local\" )
                            """)
            self.conn.commit()
            return f"{project_name} inserted into DB"
        else:
            return f"{project_name} already exists in DB"
    
    
    def create_file(self,file_meta,project_name,filekey,projectkey):
        # check if file exists
        if not self.check_existance(file_meta["abspath"],"abspath","paperclip_files"):
            object_name = project_name
            state = "upload" # "only_local"
            self.c.execute(f"""INSERT INTO paperclip_files (filekey,filename,filesize,abspath,dirpath,objectname,projectname,projectkey,state) 
                               VALUES ('{filekey}','{file_meta["filename"]}','{file_meta["filesize"]}','{file_meta["abspath"]}','{file_meta["dirpath"]}', '{object_name}' ,'{project_name}', '{projectkey}','{state}' )
                            """)
            self.conn.commit()
            return f"{file_meta['filename']} inserted into DB"
        else:
            return f"{file_meta['filename']} already exists in DB"
            
    
    
    
    
    """
    State Management DB Tools
    """
    
    def get_project(self,projectkey):
        project = self.c.execute(f"SELECT * from paperclip_projects WHERE projectkey='{projectkey}' ").fetchall()
        files = self.c.execute(f"SELECT * from paperclip_files WHERE projectkey='{projectkey}' ").fetchall()
        return project , files
    
    
    def get_files_with_state(self,project_name,state):
        results = self.c.execute(f"SELECT * from paperclip_files WHERE state='{state}' AND projectname='{project_name}' ").fetchall()
        return results
        
    def change_state_file(self,files,state):
        filekeys = [f[0] for f in files]
        for filekey in filekeys:
            results = self.c.execute(f"""
                                        UPDATE paperclip_files 
                                        SET state="{state}"
                                        WHERE filekey = "{filekey}" 
                                    """)

            self.conn.commit()
        time.sleep(1)
        
