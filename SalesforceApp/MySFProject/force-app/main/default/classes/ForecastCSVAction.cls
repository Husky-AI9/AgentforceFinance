public with sharing class ForecastCSVAction {

    // Input wrapper to be used by Flow.
    public class ForecastInput {
        @InvocableVariable(required=true label='CSV URL')
        public String csvUrl;
        
        @InvocableVariable(required=true label='Time Column')
        public String timeCol;
        
        @InvocableVariable(required=true label='Value Column')
        public String valueCol;
        
        @InvocableVariable(required=true label='Prediction Steps')
        public Integer predictionSteps;
    }
    
    // Output wrapper to return from the invocable method.
    public class ForecastOutput {
        @InvocableVariable(label='CSV Download Link')
        public String csvDownloadLink;
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
    @InvocableMethod(label='Run Forecast From CSV Document mode' description='Calls the ForecastService and returns CSV download links')
    public static List<ForecastOutput> runForecastMethod(List<ForecastInput> inputs) {
        List<ForecastOutput> results = new List<ForecastOutput>();
        // Process each input (usually just one record in a Flow)
        for (ForecastInput input : inputs) {
            // Call the existing ForecastService's static method.
            ForecastCSVService.ForecastCSVResult serviceCSVResult = ForecastCSVService.runForecastCSV(
                input.csvUrl, input.timeCol, input.valueCol, input.predictionSteps
            );

            // ForecastCSVService.ForecastCSVResult serviceCSVResult = ForecastCSVService.runForecastCSV();           
            // Populate the output wrapper.
            ForecastOutput output = new ForecastOutput();
            output.csvDownloadLink =  '<a href="' + serviceCSVResult.csvDownloadLink + '" target="_blank">Download Link</a>';
            results.add(output);
        }
        return results;
    }
}
