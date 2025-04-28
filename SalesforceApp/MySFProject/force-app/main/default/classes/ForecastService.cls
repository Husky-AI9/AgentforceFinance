public with sharing class ForecastService {

   
    // A simple wrapper class to return the links
    public class ForecastResult {
        @AuraEnabled public String pngDownloadLink;
    }

    /**
     * Runs the forecast by calling the external endpoints.
     * The method downloads the forecast PNG and CSV from the external services,
     * stores them as ContentVersion records in Salesforce, and returns downloadable links.
     *
     * @param csvUrl The URL for the original CSV file.
     * @param timeCol The name of the date/time column.
     * @param valueCol The name of the revenue/value column.
     * @param predictionSteps Number of future time steps to forecast.
     * @return ForecastResult object with both PNG and CSV download links.
     */
    public static ForecastResult runForecast(String csvUrl, String timeCol, String valueCol, Integer predictionSteps) {
        Http http = new Http();

        // Prepare POST request for the forecast PNG endpoint.
        HttpRequest reqForecast = new HttpRequest();
        reqForecast.setEndpoint('callout:FinanceChatBotCredential/forecast');
        reqForecast.setMethod('POST');
        reqForecast.setHeader('Content-Type', 'application/json');
      
        // Build JSON payload.
        String payloadBody = '{"csv_url": "' + escapeJson(csvUrl) + '",' +
                             '"time_col": "' + escapeJson(timeCol) + '",' +
                             '"value_col": "' + escapeJson(valueCol) + '",' +
                             '"prediction_steps": ' + predictionSteps + '}';

        reqForecast.setBody(payloadBody);

        HttpResponse resForecast = http.send(reqForecast);
        if (resForecast.getStatusCode() != 200) {
            throw new CalloutException('Error from forecast endpoint: ' + resForecast.getStatus());
        }
        Blob pngBlob = resForecast.getBodyAsBlob();
        
        // Store the PNG as a ContentVersion record.
        ContentVersion pngContent = new ContentVersion();
        pngContent.Title = 'ForecastImage';
        pngContent.PathOnClient = 'forecast.png';
        pngContent.VersionData = pngBlob;
        insert pngContent;
        // Retrieve the ContentVersion record.
        pngContent = [SELECT Id FROM ContentVersion WHERE Id = :pngContent.Id];

        // Create ContentDistribution for the PNG.
        ContentDistribution cdPng = new ContentDistribution();
        cdPng.ContentVersionId = pngContent.Id;
        cdPng.Name = 'Forecast PNG Distribution';
        cdPng.PreferencesNotifyOnVisit = false;
        cdPng.PreferencesLinkLatestVersion = true;
        cdPng.PreferencesAllowOriginalDownload = true;
        cdPng.PreferencesPasswordRequired = false;  // Disable password protection
        insert cdPng;
        // Query the public URL.
        cdPng = [SELECT ContentDownloadUrl FROM ContentDistribution WHERE Id = :cdPng.Id];
        String pngDownloadLink = cdPng.ContentDownloadUrl;

        // Package both download links in the return object.
        ForecastResult result = new ForecastResult();
        result.pngDownloadLink = pngDownloadLink;
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
