public with sharing class FinanceChatbotAction {
    // Inner class for the request
    public class ChatbotRequest {
        @InvocableVariable(required=true)
        public String question;
    }
    
    // Inner class for the response
    public class ChatbotResponse {
        @InvocableVariable
        public String answer;
    }

    /**
     * @description 
     *  This Invocable Method can be used in Flow to call the FinanceChatbotService
     *  and retrieve the chatbot's response.
     *
     * @param requests 
     *  A list of ChatbotRequest objects, each containing a question.
     *
     * @return 
     *  A list of ChatbotResponse objects, each containing the chatbot's answer.
     */
    @InvocableMethod(label='Get Finance Chatbot Answer' description='Calls the finance chatbot API and returns the answer')
    public static List<ChatbotResponse> getChatbotAnswer(List<ChatbotRequest> requests) {
        // Create a list to hold outputs for each request
        List<ChatbotResponse> responses = new List<ChatbotResponse>();

        for (ChatbotRequest req : requests) {
            // Use your existing service class for the callout
            String answer = FinanceChatbotService.getChatbotAnswer(req.question);
            
            // Prepare response
            ChatbotResponse res = new ChatbotResponse();
            res.answer = answer;
            responses.add(res);
        }

        return responses;
    }
}
