public with sharing class LocalDocumentService {

    /**
     * Given a URL to a document (pdfUrl), this method:
     *  1) Calls an external API (via Named Credential) passing the URL.
     *  2) Returns the text response from the endpoint.
     *
     * @param documentName A fully qualified URL to the document (PDF).
     * @return The text response from the external endpoint.
     */
    public static String sharePublicLinkAndSend(String documentName) {
        

        List<ContentVersion> contentList = [SELECT Id FROM ContentVersion WHERE Title = :documentName LIMIT 1];
        if (contentList.isEmpty()) {
            return 'No matching document found';
        }
        ContentVersion content = contentList[0];
        // Create ContentDistribution for the CSV.
        ContentDistribution cdCsv = new ContentDistribution();
        cdCsv.ContentVersionId = content.Id;
        cdCsv.Name = 'Document';
        cdCsv.PreferencesNotifyOnVisit = false;
        cdCsv.PreferencesLinkLatestVersion = true;
        cdCsv.PreferencesAllowOriginalDownload = true;
        cdCsv.PreferencesPasswordRequired = false;  // Disable password protection
        insert cdCsv;
        try{
            cdCsv = [SELECT ContentDownloadUrl FROM ContentDistribution WHERE Id = :cdCsv.Id];
        }
        catch (QueryException qe) {
            System.debug('QueryException2: ' + qe.getMessage());
            return 'Error1';
            // Optionally, rethrow or handle the exception as required.
        }
        String csvDownloadLink = cdCsv.ContentDownloadUrl;

        // Ensure you handle cases where no record is found.
        if (cdCsv == null) {
            System.debug('No matching document found with name: ' + documentName);
            return 'No matching document found';
        }
        return csvDownloadLink;
    }
}
