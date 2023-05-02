const AWS = require('aws-sdk');
const https = require('https');
const url = require('url');

const sendResponse = async (event, context, responseStatus, responseData) => {
  const responseBody = JSON.stringify({
    Status: responseStatus,
    Reason: `See the details in CloudWatch Log Stream: ${context.logStreamName}`,
    PhysicalResourceId: context.logStreamName,
    StackId: event.StackId,
    RequestId: event.RequestId,
    LogicalResourceId: event.LogicalResourceId,
    Data: responseData,
  });

  const parsedUrl = url.parse(event.ResponseURL);
  const options = {
    hostname: parsedUrl.hostname,
    port: 443,
    path: parsedUrl.path,
    method: 'PUT',
    headers: {
      'Content-Type': '',
      'Content-Length': responseBody.length,
    },
  };

  return new Promise((resolve, reject) => {
    const request = https.request(options, (response) => {
      if (response.statusCode >= 200 && response.statusCode < 300) {
        resolve();
      } else {
        reject(new Error(`Unexpected status code: ${response.statusCode}`));
      }
    });

    request.on('error', (error) => {
      reject(error);
    });

    request.write(responseBody);
    request.end();
  });
};

exports.handler = async (event, context) => {
  console.log('Received event:', JSON.stringify(event, null, 2));

  const responseData = { randomNumber: Math.floor(Math.random() * 100) + 1 };

  try {
    await sendResponse(event, context, 'SUCCESS', responseData);
  } catch (error) {
    console.error('Failed to send response:', error);
    await sendResponse(event, context, 'FAILED', {});
  }
};
