public with sharing class InvoiceCompareService {

    /**
     * Given URLs to an invoice and a purchase order, this method:
     *  1) Calls an external API (via Named Credential) passing both URLs.
     *  2) Returns the text response from the endpoint.
     *
     * @param invoiceUrl       A fully qualified URL to the invoice PDF.
     * @param purchaseOrderUrl A fully qualified URL to the purchase order PDF.
     * @return The text response from the external endpoint.
     */
    @AuraEnabled
    public static String sharePublicLinkAndSend(String invoiceUrl, String purchaseOrderUrl) {
        // 1) Set up the HTTP request
        HttpRequest req = new HttpRequest();
        // 'FinanceChatBotCredential' must be a Named Credential pointing to your service
        // We're now calling '/analyze-invoice'
        req.setEndpoint('callout:FinanceChatBotCredential/analyze-invoice');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json;charset=UTF-8');

        // 2) Construct the JSON payload with both URLs
        Map<String, String> payload = new Map<String, String>{
            'invoice_url'        => invoiceUrl,
            'purchase_order_url' => purchaseOrderUrl
        };
        req.setBody(JSON.serialize(payload));

        // 3) Send the HTTP callout
        Http http = new Http();
        HttpResponse res;
        try {
            res = http.send(req);
        } catch (System.CalloutException e) {
            throw new AuraHandledException('External callout failed: ' + e.getMessage());
        }

        // 4) Parse and return the endpoint response
        // Assuming the service returns JSON like { "result": "…summary text…" }
        Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        String summary = (String) parsed.get('result');
        return summary;
    }
}
