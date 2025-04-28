public with sharing class LocalDocumentAction {
    // Inner class for the request
    public class Request {
        @InvocableVariable(required=true)
        public String documentName;
    }
    
    // Inner class for the response
    public class Response {
        @InvocableVariable
        public String answer;
    }

    /**
     * @description 
     *  This Invocable Method can be used in Flow to call the FinanceChatbotService
     *  and retrieve the chatbot's response.
     *
     * @param requests 
     *  A list of Request objects, each containing a question.
     *
     * @return 
     *  A list of Response objects, each containing the chatbot's answer.
     */
    @InvocableMethod(label='Analyze Internal Finnance Document' description='Analyze internal financial statement and make a summary')
    public static List<Response> sharePublicLinkAndSend(List<Request> requests) {
        // Create a list to hold outputs for each request
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            // Use your existing service class for the callout
            String answer = LocalDocumentService.sharePublicLinkAndSend(req.documentName);
            
            // Prepare response
            Response res = new Response();
            res.answer = answer;
            responses.add(res);
        }

        return responses;
    }
}
