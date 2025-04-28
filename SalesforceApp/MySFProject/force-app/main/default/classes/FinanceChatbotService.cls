public with sharing class FinanceChatbotService {
    /**
     * Calls the finance chatbot endpoint using a Named Credential
     * named 'FinanceChatBotCredential'.
     */
    @AuraEnabled(cacheable=false)
    public static String getChatbotAnswer(String userQuestion) {
        if (String.isBlank(userQuestion)) {
            return 'No question was provided.';
        }
        
        try {
            // Construct the HTTP request
            HttpRequest req = new HttpRequest();

            /*
             * If you have a Named Credential called 'FinanceChatBotCredential'
             * and your path to the endpoint is '/finance-chatbot', then
             * the final URL becomes:
             *    https://your-app.onrender.com/finance-chatbot
             *   (assuming your Named Credential's URL is https://your-app.onrender.com)
             */
            req.setEndpoint('callout:FinanceChatBotCredential/finance-chatbot');
            req.setMethod('POST');
            req.setHeader('Content-Type', 'application/json');
            
            // Build the JSON body. Escape quotes to avoid errors.
            String requestBody = '{"question": "' + String.escapeSingleQuotes(userQuestion) + '"}';
            req.setBody(requestBody);
            
            // Send the request
            Http http = new Http();
            HTTPResponse res = http.send(req);
            
            // Check the status code
            if (res.getStatusCode() == 200) {
                // The response is expected to look like: {"answer": "..."}
                Map<String, Object> responseMap = 
                    (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
                
                if (responseMap.containsKey('answer')) {
                    return (String)responseMap.get('answer');
                } else {
                    return 'No "answer" field found in response.';
                }
            } else {
                // Non-200 response
                return 'Error: Status code ' + res.getStatusCode() +
                       '. Body: ' + res.getBody();
            }
        } catch (Exception e) {
            return 'Exception while calling the chatbot: ' + e.getMessage();
        }
    }
}