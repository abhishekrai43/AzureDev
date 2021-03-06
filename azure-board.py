# Author:- Abhishek Rai
# Env:- Python 3.9.0


# Import Libraries
import json
import requests
import base64
import re
import sqlite3
from decouple import config
from az_sql_db import create_db
from pathlib import Path


# Set Organization and Personal Access Token
organization = "https://dev.azure.com/pursuitsoftwaredev"
# noinspection SpellCheckingInspection
pat = config('pat',default='')
authorization = str(base64.b64encode(bytes(':'+pat, 'ascii')), 'ascii')

# Set Authentication Headers
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Basic '+authorization
}
project_names = []
# Get Project Names All

projects = requests.get(url="https://dev.azure.com/pursuitsoftwaredev/_apis/projects?api-version=5.1", headers=headers).json()
for item in projects['value']:
    project_names.append(item['name'])
my_file = Path("Azure_Board.db")
if not my_file.is_file():
    # Create the Database
    create_db()

# noinspection SpellCheckingInspection
CLEANR = re.compile('<.*?>')

# noinspection SpellCheckingInspection
# Remove HTML Tags from Description


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return str(cleantext)

# noinspection SpellCheckingInspection
# Get Work Item Details
def widet(resp, table, id):
    # Work Item Title
    wi_title = resp['value'][0]['fields']['System.Title']['newValue']
    
    # Created On
    created_on = resp['value'][0]['fields']['System.CreatedDate']['newValue']
    
    # Name
    wi_name = resp['value'][0]['revisedBy']['displayName']
    
    # Email Address
    wi_email = resp['value'][0]['revisedBy']['name']
    
    # WI State
    wi_state = resp['value'][0]['fields']['System.State']['newValue']
    
    # WI Reason
    wi_reason = resp['value'][0]['fields']['System.Reason']['newValue']
    
    # WI Area
    wi_area = resp['value'][0]['fields']['System.AreaPath']['newValue']
    
    # WI Iteration
    wi_iteration = resp['value'][0]['fields']['System.IterationPath']['newValue']
    
    # WI Comments
    comments = resp['value'][0]['fields']['System.CommentCount']['newValue']
    
    # WI Priority
    priority = resp['value'][0]['fields']['Microsoft.VSTS.Common.Priority']['newValue']
    
    # WI Value Area

    try:
        wi_val_area = resp['value'][0]['fields']['Microsoft.VSTS.Common.ValueArea']['newValue']
        
    except:
        wi_val_area = ''

    # WI Description
    try:
        wi_description = resp['value'][0]['fields']['System.Description']['newValue']
        clean_desc = cleanhtml(wi_description)
        
    except:
        wi_description = ''
    connection = sqlite3.connect("Azure_Board.db")
    crsr = connection.cursor()
    # SQL command to insert the data in the table
    if table == 'TestCase':
        # Get Steps
        t_steps = resp['value'][0]['fields']['Microsoft.VSTS.TCM.Steps']['newValue']
        clean_tsteps = cleanhtml(t_steps)
        # Remove unwanted tags
        unwt = ['&lt;', 'DIV&gt;', 'P&gt;', '//']
        for unw in unwt:
            clean_tsteps = clean_tsteps.replace(unw, '')

        auto_stat = resp['value'][0]['fields']['Microsoft.VSTS.TCM.AutomationStatus']['newValue']
        
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,Microsoft_VSTS_Common_ValueArea, Steps, Automation) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id ,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority, wi_val_area, clean_tsteps, auto_stat)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'Task':
        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
            
        except:
            clean_desc = ''
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,System_Description) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority, clean_desc)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'UserStory':
        try:
            story_points = resp['value'][0]['fields']['Microsoft.VSTS.Scheduling.StoryPoints']['newValue']
        except:
            story_points = ''
        try:
            req_id = resp['value'][0]['fields']['Custom.QtestRequirementID']['newValue']
        except:
            req_id = ''
        # Acceptance Criteria
        try:
            wi_criteria = resp['value'][0]['fields']['Microsoft.VSTS.Common.AcceptanceCriteria']['newValue']
            clean_crit = cleanhtml(wi_criteria)
        
        except:
            clean_crit = ''
        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
            
        except:
            clean_desc = ''
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,Microsoft_VSTS_Common_ValueArea,Story_Points,Requirement_ID,Microsoft_VSTS_Common_AcceptanceCriteria,System_Description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority, wi_val_area,story_points,req_id,clean_crit, clean_desc)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'Bug':
        # Bug Severity
        b_severity = resp['value'][0]['fields']['Microsoft.VSTS.Common.Severity']['newValue']
    
        # Defect ID
        try:
            def_id = resp['value'][0]['fields']['Custom.qTestDefect_Id']['newValue']
        
        except:
            def_id = ''
        # Repro Steps
        try:
            wi_repr = resp['value'][0]['fields']['Microsoft.VSTS.TCM.ReproSteps']['newValue']
            clean_repr = cleanhtml(wi_repr)
        
        except:
            clean_repr = ''
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,Microsoft_VSTS_Common_Severity,Defect_ID,Microsoft_VSTS_TCM_ReproSteps,System_Description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority,b_severity,def_id,clean_repr, wi_description)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'Product_Backlog_Item':

        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
           
        except:
            clean_desc = ''
        # Acceptance Criteria
        try:
            wi_criteria = resp['value'][0]['fields']['Microsoft.VSTS.Common.AcceptanceCriteria']['newValue']
            clean_crit = cleanhtml(wi_criteria)
        
        except:
            clean_crit = ''
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,Microsoft_VSTS_Common_ValueArea,System_Description, Microsoft_VSTS_Common_AcceptanceCriteria) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority,wi_val_area,clean_desc, clean_crit)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'Issue':

        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
        
        except:
            clean_desc = ''
        # Acceptance Criteria
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,System_Description) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority,clean_desc)
        crsr.execute(sql_command, data_tuple)
        connection.commit()
    elif table == 'Epic':

        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
        
        except:
            clean_desc = ''

        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,System_Description) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id,wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority, clean_desc)
        crsr.execute(sql_command, data_tuple)
        connection.commit()

    elif table == 'Feature':

        # WI Description
        try:
            wi_description = resp['value'][0]['fields']['System.Description']['newValue']
            clean_desc = cleanhtml(wi_description)
        
        except:
            clean_desc = ''
        # Acceptance Criteria
        try:
            wi_criteria = resp['value'][0]['fields']['Microsoft.VSTS.Common.AcceptanceCriteria']['newValue']
            clean_crit = cleanhtml(wi_criteria)
    
        except:
            clean_crit = ''
        try:
            module_id = resp['value'][0]['fields']['Custom.qTestModuleID']['newValue']
        except:
            module_id = ''
        sql_command = f"INSERT INTO {table} (workItemId,System_Title,displayName,name,revisedDate,System_State,System_Reason,System_AreaPath,System_IterationPath,Microsoft_VSTS_Common_Priority,Module_ID,Microsoft_VSTS_Common_ValueArea,System_Description, Microsoft_VSTS_Common_AcceptanceCriteria) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        data_tuple = (id, wi_title, wi_name, wi_email, created_on, wi_state, wi_reason, wi_area, wi_iteration, priority, module_id, wi_val_area, clean_desc, clean_crit)
        crsr.execute(sql_command, data_tuple)
        connection.commit()


# noinspection SpellCheckingInspection
# Get Relations
def relations(pro, woid):
    connection = sqlite3.connect("Azure_Board.db")
    crsr = connection.cursor()
    relati = requests.get(f'https://dev.azure.com/pursuitsoftwaredev/{pro}/_apis/wit/workitems/{woid}/?$expand=relations&api-version=6.0', headers=headers).json()
    try:
        for ite in relati['relations']:
            rel_name = ite['attributes']['name']
            w_id = ite['url'][-3:]
            if w_id.isdigit():
                resp = requests.get(f'https://dev.azure.com/pursuitsoftwaredev/{pro}/_apis/wit/workItems/{w_id}/updates?api-version=6.0', headers=headers).json()
                # Work Item Type
                wit_type = resp['value'][0]['fields']['System.WorkItemType']['newValue']
                sql_com = f"INSERT INTO WI_Relations (workItemId,name,rel_id,System_WorkItemType) VALUES(?,?,?,?);"
                data = (woid, rel_name, w_id, wit_type)
                crsr.execute(sql_com, data)
                connection.commit()
    except:
        pass


# noinspection SpellCheckingInspection
# Get the number of revisions
def get_revisions(pro,wid):
    global operation
    connection = sqlite3.connect("Azure_Board.db")
    crsr = connection.cursor()
    get_rev = requests.get(f'https://dev.azure.com/pursuitsoftwaredev/{pro}/_apis/wit/workitems/{wid}/updates?api-version=6.0', headers=headers).json()
    revs = int(get_rev['count'])
    if revs > 1:
        for i in range(1, revs):
            ans = get_rev['value'][i]
            rev_name = ans['revisedBy']['name']
            rev_date = ans['revisedDate']
            vals = []
            changes = []
            operation = 'Added'
            try:
                for k, v in get_rev['value'][i]['fields'].items():
                    changes.append(k)
                    val = v['newValue']
                    if val == 'Approved':
                        operation = 'Updated'
                    if 'System.AssignedTo' in k:
                        operation = 'changed Assign'
                    if isinstance(val, dict):
                        vals.append(v['newValue']['displayName'])
                    else:
                        vals.append(val)
            except:
                pass

            data = [wid, i, rev_name, rev_date, operation]
            # crsr.execute(sql_comm, data)
            sql_com2 = "INSERT INTO Revisions (workItemId,rev,System_RevisedBy,System_ChangedDate,Operation,Field,new_value) VALUES(?, ?, ?, ?, ?,?, ?)"
            for elem in zip(changes, vals):
                crsr.execute(sql_com2, data + list(elem))
            connection.commit()


# noinspection SpellCheckingInspection
for project in project_names:
    wiql_query = {
            "query": f"Select [System.Id] From WorkItems Where [System.WorkItemType] <> '' AND [System.AreaPath] UNDER \'{project}\'"
        }
    # Return Work Item IDs
    work_it_req = requests.post(f"https://dev.azure.com/pursuitsoftwaredev/{project}/_apis/wit/wiql?api-version=6.0", data=json.dumps(wiql_query), headers=headers).json()
    
    for item in work_it_req['workItems']:
        wid = item['id']
        response = requests.get(f'https://dev.azure.com/pursuitsoftwaredev/{project}/_apis/wit/workItems/{wid}/updates?api-version=6.0', headers=headers).json()
        # Work Item Type
        wi_type = response['value'][0]['fields']['System.WorkItemType']['newValue']


        if wi_type == 'Test Case':
            tab = 'TestCase'
            widet(response, tab, wid)
            relations(project, wid)
            get_revisions(project, wid)

        elif wi_type == 'User Story':
            tab = 'UserStory'
            widet(response, tab, wid)
            relations(project, wid)
            get_revisions(project, wid)

        elif wi_type == 'Product Backlog Item':
            tab = 'Product_Backlog_Item'
            widet(response, tab, wid)
            relations(project, wid)
            get_revisions(project, wid)

        else:
            widet(response, wi_type, wid)
            relations(project, wid)
            get_revisions(project, wid)