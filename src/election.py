import boto3
from os import environ as env


#
#  Public functions
#


def lambda_handler(event, context):
    as_group_name = env['AUTO_SCALING_GROUP_NAME']
    instance_name = env['INSTANCE_NAME']

    print('Auto scaling group name: {s}'.format(s=as_group_name))
    print('Instance name filter: {s}'.format(s=instance_name))

    ec2 = boto3.resource('ec2')
    asc = boto3.client('autoscaling')

    instances = list(ec2.instances.filter(
        Filters=[
            {'Name': 'instance-state-name',
                'Values': ['running', 'stopping', 'stopped', 'pending']},
            {'Name': 'tag:Name',
                'Values': [instance_name]}
        ]
    ).all())

    for i in instances:
        print('Found instance: {s}'.format(s=i.id))

    primary = __find_primary(instances)

    if primary:
        print('Found primary: {s}'.format(s=primary.id))
    else:
        print('Failed to find primary.')
        primary = instances[0]
        print('Assigned primary: {s}'.format(s=primary.id))

    print('Setting primary tag.')
    ec2.create_tags(Resources=[primary.id],
                    Tags=[{'Key': 'primary', 'Value': 'primary'}])

    print('Setting instance protection.')
    asc.set_instance_protection(InstanceIds=[primary.id],
                                AutoScalingGroupName=as_group_name,
                                ProtectedFromScaleIn=True)

    return True


#
# Private functions.
#


def __find_primary(instances):
    for instance in instances:
        for tag in instance.tags:
            if tag['Key'] == 'primary':
                return instance

    return None
