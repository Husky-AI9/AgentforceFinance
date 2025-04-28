public with sharing class ExtractInvoiceService {

    // A simple wrapper class to return the links
    public class result {
        @AuraEnabled public String downloadLink;
    }
    public static result extractInvoice(String url) {
        Http http = new Http();
        Map<String, String> payload = new Map<String, String>{
            'invoice_url' => url
        };
        // Prepare GET request for the forecast CSV endpoint.
        HttpRequest reqForecast = new HttpRequest();
        reqForecast.setEndpoint('callout:FinanceChatBotCredential/extract-invoice');
        reqForecast.setMethod('POST');
        reqForecast.setHeader('Content-Type', 'application/json');
        reqForecast.setBody(JSON.serialize(payload));

        HttpResponse resCsv = http.send(reqForecast);
        if (resCsv.getStatusCode() != 200) {
            throw new CalloutException('Error: ' + resCsv.getStatus());
        }
        Blob csvBlob = resCsv.getBodyAsBlob();

        ContentVersion csvContent = new ContentVersion();
        csvContent.Title = 'ExtractedInvoice';
        csvContent.PathOnClient = 'ExtractedInvoice.csv';
        csvContent.VersionData = csvBlob;
        insert csvContent;
        csvContent = [SELECT Id FROM ContentVersion WHERE Id = :csvContent.Id];

        // Create ContentDistribution for the CSV.
        ContentDistribution cdCsv = new ContentDistribution();
        cdCsv.ContentVersionId = csvContent.Id;
        cdCsv.Name = 'ExtractedInvoice Distribution';
        cdCsv.PreferencesNotifyOnVisit = false;
        cdCsv.PreferencesLinkLatestVersion = true;
        cdCsv.PreferencesAllowOriginalDownload = true;
        cdCsv.PreferencesPasswordRequired = false;  // Disable password protection
        insert cdCsv;
        cdCsv = [SELECT ContentDownloadUrl FROM ContentDistribution WHERE Id = :cdCsv.Id];
        String downloadLink = cdCsv.ContentDownloadUrl;
        
        // Package both download links in the return object.
        result results = new result();
        results.downloadLink = downloadLink;
        return results;
    }
}
