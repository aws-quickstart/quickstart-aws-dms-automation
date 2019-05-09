import cfnresponse
import json
import boto3

def lambda_handler(event, context):
    source_endpoint = event['ResourceProperties']['SourceArn']
    target_endpoint = event['ResourceProperties']['TargetArn']
    replication_inst = event['ResourceProperties']['ReplicationInstanceArn']
    if 'Create' or 'Update' in event['RequestType']:
        print ('This is a %s event' %(event['RequestType']))
        print('Checking connection for Source .....')
        source_result = check_connection(source_endpoint,replication_inst)
        print('Source result was %s' %(source_result))
        if 'success' in source_result:
            print('Proceeding to check connection for Target ....')
            target_result = check_connection(target_endpoint,replication_inst)
            print('Target result was %s' %(target_result))
            if 'success' in target_result:
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, '')
            else:
                print('Target connection failed')
                cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')
        else:
            print('Source connection failed')
            cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')
    else:
        print('Delete event nothing will be done')
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')
def check_connection(endpoint,rep):
    dms = boto3.client('dms')
    dms.test_connection(ReplicationInstanceArn=rep,EndpointArn=endpoint)
    waiter = dms.get_waiter('test_connection_succeeds')
    waiter.wait(
        Filters=[
            {
                'Name': 'endpoint-arn',
                'Values': [endpoint]
            },
            {
                'Name': 'replication-instance-arn',
                'Values':[rep]
            }
        ]
    )
    status_conn_api = dms.describe_connections(
        Filters=[
            {
                'Name': 'endpoint-arn',
                'Values': [endpoint]
            },
            {
                'Name': 'replication-instance-arn',
                'Values': [rep]
            }
        ]
    )
    stat_task = status_conn_api['Connections'][0]['Status']
    print('The connection test was %s' %(stat_task))
    return (stat_task)
