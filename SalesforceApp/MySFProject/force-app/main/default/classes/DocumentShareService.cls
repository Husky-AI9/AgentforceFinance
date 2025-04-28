public with sharing class DocumentShareService {

    /**
     * Given a URL to a document (pdfUrl), this method:
     *  1) Calls an external API (via Named Credential) passing the URL.
     *  2) Returns the text response from the endpoint.
     *
     * @param pdfUrl A fully qualified URL to the document (PDF).
     * @return The text response from the external endpoint.
     */
    public static String sharePublicLinkAndSend(String pdfUrl) {
        // 1) Set up the HTTP request
        HttpRequest req = new HttpRequest();
        // 'FinanceChatBotCredential' must be a Named Credential pointing to https://agentforcefinance.onrender.com
        // We'll append '/analyze-document' as the path:
        req.setEndpoint('callout:FinanceChatBotCredential/analyze-document');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json;charset=UTF-8');

        // 2) Construct the JSON payload with the URL
        Map<String, String> payload = new Map<String, String>{
            'url' => pdfUrl
        };
        req.setBody(JSON.serialize(payload));

        // 3) Send the HTTP callout
        Http http = new Http();
        HttpResponse res;
        try {
            res = http.send(req);
        } catch (System.CalloutException e) {
            // Handle callout exception if needed
            throw new AuraHandledException('External callout failed: ' + e.getMessage());
        }

        // 4) The endpoint response is text
        Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        String textOnly = (String) parsed.get('response');
        return textOnly;    }
}
