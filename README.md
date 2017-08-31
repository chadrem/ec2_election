# ec2_election
AWS EC2 Auto Scaling leader election using AWS Lambda and Python 2.7.

## Background
This project will automatically choose a leader instance for your AWS Auto Scaling group.
It will then tag the leader as "primary" and configure the instance to avoid being terminated.

## Why
In many cases you need a single leader instance to perform tasks.
An example is to run a script daily at a specific time.

## Code
The code in ````election.py```` is an AWS Lambda function (Python 2.7).
It requires two instance variables to be set:

* ````AUTO_SCALING_GROUP_NAME````: The group name of the auto scaling instance.
* ````INSTANCE_NAME````: The tag Name value for all of the instances you want to consider for leadership.

Also included in ````tasks.py```` are a set of [Invoke](http://www.pyinvoke.org) tasks:

* ````invoke execute --group <group_name> --instance <instance_tag_name>````: Execute the election code locally. Useful for testing parameters and making code changes.
* ````invoke release --bucket <bucket_name> --function <function_name>````: Create a release zip file, upload it to S3, update AWS Lambda for the new S3 file, and finally execute the funtion.

## Automation
You have *two choices* for when to execute the Lambda function:

* *On a periodic schedule*. This solution uses CloudWatch scheduled events. See this [tutorial](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html) to create a simple event (example every 15 minutes) to automatically execute the Lambda function.
* *When Auto Scaling generates an event*. This solution uses Auto Scaling events with an SNS Topic. See this [tutorial](https://ajbrown.org/2017/02/10/leader-election-with-aws-auto-scaling-groups.html) for more information.

## Instance code
The code running on your instances should query the EC2 API to look for a tag indicating it is the leader.
The leader will have a tag with the Key = primary and Value = primary.
