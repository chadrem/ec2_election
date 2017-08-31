from invoke import task
from src import election
from os import environ as env, chdir
from time import gmtime, strftime
from sys import exit
import boto3
import base64


@task(default=True)
def execute(ctx, group=None, instance=None):
    if not group:
        print('You must specify an auto scaling group name with --group')
        exit(1)

    if not instance:
        print('You must specify an instance tag Name with --instance')
        exit(1)

    env['AUTO_SCALING_GROUP_NAME'] = group
    env['INSTANCE_NAME'] = instance
    election.lambda_handler({}, None)


@task
def release(ctx, bucket=None, function=None):
    chdir('src')

    if not bucket:
        print('You must specify a bucket name with --bucket')
        exit(1)

    if not function:
        print('You must specify a funtion name with --function')
        exit(1)

    s3 = boto3.client('s3')
    lam = boto3.client('lambda')
    file_time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    file_name = 'release_' + file_time + '.zip'
    file_name_path = '../build/' + file_name
    print('Release: {s}'.format(s=file_name))

    print('Compressing...')
    ctx.run('zip -rq9 {fnp} .'.format(fnp=file_name_path))

    print('Uploading...')
    s3.upload_file(file_name_path, bucket, file_name)

    print('Updating function code...')
    lam.update_function_code(S3Bucket=bucket,
                                  S3Key=file_name,
                                  FunctionName=function)

    print('Invoking (look for errors)...')
    resp = lam.invoke(FunctionName=function,
                      InvocationType='RequestResponse', LogType='Tail')
    print(base64.b64decode(resp['LogResult']))
