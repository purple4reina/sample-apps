import { Handler } from 'aws-lambda';

export const handler: Handler = async (event, context) => {
    return JSON.stringify(event, null, 2);
};
