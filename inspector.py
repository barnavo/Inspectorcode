'''
Author:Barnavo Chowdhury
Date:30/05/2019
'''


import json
import boto3
import uuid
import os
import time

ssmClient = boto3.client('ssm')
inspectorClient = boto3.client('inspector')
suffix = uuid.uuid4()
ruleARN = str(os.environ['rulearn'])

invokeLam = boto3.client("lambda", region_name="us-east-2")

def lambda_handler(event, context):
    try:
        agent_install = ssmClient.send_command(
        Targets=[
        {
            'Key': 'tag:OS',
            'Values': [
                'Linux'
            ]
        },
        ],
         DocumentName='AmazonInspector-ManageAWSAgent',
         Parameters={"Operation":["Install"]})
        
        time.sleep(180)
       
        try:
            resourcegrpcreate = inspectorClient.create_resource_group(
            resourceGroupTags=[
            {
                'key': 'OS',
                'value': 'Linux',
            },
            ],
            )
        
            resourceGroupArn = resourcegrpcreate['resourceGroupArn']
            
        except Exception as e:
            print(e)
            
        try:
            assessmentcrtTarget = inspectorClient.create_assessment_target(
            assessmentTargetName='testassessmenttarget'+ str(suffix),
            resourceGroupArn=resourceGroupArn
            )
            assessmentTargetArn = assessmentcrtTarget['assessmentTargetArn']
            
        except Exception as e:
            print(e)
        
        
        try:
            assessmentTemplate = inspectorClient.create_assessment_template(
            assessmentTargetArn=assessmentTargetArn,
            assessmentTemplateName='testassessmenttemplate'+ str(suffix),
            durationInSeconds=180,
            rulesPackageArns=[ ruleARN ]
            )
    
            assessmentTemplateArn=assessmentTemplate['assessmentTemplateArn']
            
        except Exception as e:
            print(e)
        
        
        try:
            start_assessment_run = inspectorClient.start_assessment_run(
            assessmentRunName='examplerun',
            assessmentTemplateArn=assessmentTemplateArn,
            )

            myassessment = start_assessment_run['assessmentRunArn']
            print(myassessment)
        
        except Exception as e:
            print(e)
    
        payload = { 'myassessmentarn' : myassessment }
        time.sleep(360)
        
        try:
            resp=invokeLam.invoke(FunctionName="lambdainspectorreport", InvocationType= "Event", Payload=json.dumps(payload))
        except Exception as e:
            print(e)
            
            
    except Exception as e:
        print(e)
    
    
    
