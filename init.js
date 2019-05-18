// This user is limited to the EduPass Lambda function, which handles authorization within the function
AWS.config.accessKeyId = 'AKIAQF4IUI6AIH5HNSOF';
AWS.config.secretAccessKey = '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';
AWS.config.region = 'ap-southeast-1';
const LAMBDA = new AWS.Lambda({apiVersion: '2015-03-31'});