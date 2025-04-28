public with sharing class ExtractInvoiceAction {

    // Input wrapper to be used by Flow.
    public class ExtractInvoiceInput {
        @InvocableVariable(required=true label='CSV URL')
        public String url;
    }
    
    // Output wrapper to return from the invocable method.
    public class ExtractInvoiceOutput {
        @InvocableVariable(label='Downloads Link')
        public String downloadLink;
    }
    
    /**
     * Invocable method to run the forecast.
     * The method accepts a list of ForecastInput (typically a single record),
     * calls the ForecastService.runForecast method, and returns a list of ForecastOutput
     * containing downloadable links to the forecast PNG and CSV files.
     *
     * @param inputs List of ForecastInput records provided by Flow.
     * @return List of ForecastOutput records with the download links.
     */
    @InvocableMethod(label='Extract Invoice into CSV' description='Calls the ExtractInvoiceService and return downloadable url link')
    public static List<ExtractInvoiceOutput> extractInvoiceMethod(List<ExtractInvoiceInput> inputs) {
        List<ExtractInvoiceOutput> results = new List<ExtractInvoiceOutput>();
        // Process each input (usually just one record in a Flow)
        for (ExtractInvoiceInput input : inputs) {
            // Call the existing ForecastService's static method.
            ExtractInvoiceService.result serviceResult = ExtractInvoiceService.extractInvoice(input.url);
            ExtractInvoiceOutput output = new ExtractInvoiceOutput();
            output.downloadLink =  '<a href="' + serviceResult.downloadLink + '" target="_blank">Download Link</a>';
            results.add(output);
        }
        return results;
    }
}
