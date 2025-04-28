public with sharing class ForecastCSVService {

    // A simple wrapper class to return the links
    public class ForecastCSVResult {
        @AuraEnabled public String csvDownloadLink;
    }
    public static ForecastCSVResult runForecastCSV(String csvUrl, String timeCol, String valueCol, Integer predictionSteps) {
        Http http = new Http();

        
        // Build JSON payload.
        String payloadBody = '{"csv_url": "' + escapeJson(csvUrl) + '",' +
                             '"time_col": "' + escapeJson(timeCol) + '",' +
                             '"value_col": "' + escapeJson(valueCol) + '",' +
                             '"prediction_steps": ' + predictionSteps + '}';
        
        // Prepare GET request for the forecast CSV endpoint.
        HttpRequest reqForecast = new HttpRequest();
        reqForecast.setEndpoint('callout:FinanceChatBotCredential/forecast_csv');
        reqForecast.setMethod('POST');
        reqForecast.setHeader('Content-Type', 'application/json');
        reqForecast.setBody(payloadBody);

        HttpResponse resCsv = http.send(reqForecast);
        if (resCsv.getStatusCode() != 200) {
            throw new CalloutException('Error from forecast CSV endpoint: ' + resCsv.getStatus());
        }
        Blob csvBlob = resCsv.getBodyAsBlob();

        // Store the CSV as a ContentVersion record.
        ContentVersion csvContent = new ContentVersion();
        csvContent.Title = 'ForecastCSV';
        csvContent.PathOnClient = 'forecasted.csv';
        csvContent.VersionData = csvBlob;
        insert csvContent;
        csvContent = [SELECT Id FROM ContentVersion WHERE Id = :csvContent.Id];

        // Create ContentDistribution for the CSV.
        ContentDistribution cdCsv = new ContentDistribution();
        cdCsv.ContentVersionId = csvContent.Id;
        cdCsv.Name = 'Forecast CSV Distribution';
        cdCsv.PreferencesNotifyOnVisit = false;
        cdCsv.PreferencesLinkLatestVersion = true;
        cdCsv.PreferencesAllowOriginalDownload = true;
        cdCsv.PreferencesPasswordRequired = false;  // Disable password protection
        insert cdCsv;
        cdCsv = [SELECT ContentDownloadUrl FROM ContentDistribution WHERE Id = :cdCsv.Id];
        String csvDownloadLink = cdCsv.ContentDownloadUrl;
        
        // Package both download links in the return object.
        ForecastCSVResult result = new ForecastCSVResult();
        result.csvDownloadLink = csvDownloadLink;
        return result;
    }

    // Helper method to escape JSON string values.
    private static String escapeJson(String input) {
        if(input == null) {
            return '';
        }
        // This is a very basic escaping implementation.
        return input.replace('\\', '\\\\').replace('"', '\\"');
    }
    
}
