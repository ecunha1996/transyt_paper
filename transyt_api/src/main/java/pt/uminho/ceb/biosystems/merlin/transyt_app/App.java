package pt.uminho.ceb.biosystems.merlin.transyt_app;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.TimeUnit;

import pt.uminho.ceb.biosystems.mew.utilities.io.FileUtils;


public class App {
    public static void main(String[] args) {
        //FILES MUST BE SUBMITTED IN THE FOLLOWING ORDER: 1.PROTEOME -> 2.MODEL or METABOLITES

        // Scerevisiae   Paeruginosa    Blongum    Olucimarinus

        String[] caseStudies = {"Scerevisiae", "Paeruginosa", "Blongum", "Olucimarinus"};
        //String[] caseStudies = {"Blongum"};

        HashMap<String, Long> taxonomyIDs = new HashMap<>();

        taxonomyIDs.put("Scerevisiae", 559292L);
        taxonomyIDs.put("Paeruginosa", 208964L);
        taxonomyIDs.put("Blongum", 890402L);
        taxonomyIDs.put("Olucimarinus", 436017L);

        String mode = "relaxed"; //default

        for (String caseStudy : caseStudies) {

            String transytDirectory = "C:\\Users\\Bisbii\\Desktop\\TranSyt\\case_study\\" + caseStudy + "\\" + mode + "\\";

            if (!new File(transytDirectory).exists())
                new File(transytDirectory).mkdirs();

            File compoundsFile = new File("C:\\Users\\Bisbii\\Desktop\\TranSyt\\case_study\\kegg_compounds.txt");
            File genomeFile = new File("C:\\Users\\Bisbii\\Desktop\\TranSyt\\case_study\\" + caseStudy + "\\protein.faa");

            assert compoundsFile.exists();
            assert genomeFile.exists();

            List<File> requiredFiles = new ArrayList<>();

            requiredFiles.add(genomeFile);
            requiredFiles.add(compoundsFile);

            long taxonomyID = taxonomyIDs.get(caseStudy);

            System.out.println("submitting files..." + caseStudy);

            HashMap<String, String> userInputs = new HashMap<>();
            if (mode.equals("default")) {
                userInputs.put("reference_database", "KEGG");
                userInputs.put("override_ontologies_filter", "false");
                userInputs.put("alpha", "0.75");
                userInputs.put("beta", "0.3");
                userInputs.put("minimum_hits_penalty", "2");
                userInputs.put("bitscore_threshold", "50");
                userInputs.put("query_coverage_threshold", "80");
                userInputs.put("blast_evalue_threshold", "1e-50");
                userInputs.put("score_threshold", "0.60");
                userInputs.put("similarity_score", "30");
                userInputs.put("alpha_families", "0.4");
                userInputs.put("auto_accept_evalue", "0");
                userInputs.put("percent_accept", "10");
                userInputs.put("limit_evalue_accept", "1e-20");
                userInputs.put("ignore_method2", "false");
            } else {
                userInputs.put("reference_database", "KEGG");
                userInputs.put("override_ontologies_filter", "false");
                userInputs.put("alpha", "0.75");
                userInputs.put("beta", "0.3");
                userInputs.put("minimum_hits_penalty", "2");
                userInputs.put("bitscore_threshold", "40");
                userInputs.put("query_coverage_threshold", "60");
                userInputs.put("blast_evalue_threshold", "1e-8");
                userInputs.put("score_threshold", "0.50");
                userInputs.put("similarity_score", "25");
                userInputs.put("alpha_families", "0.4");
                userInputs.put("auto_accept_evalue", "1e-20");
                userInputs.put("percent_accept", "10");
                userInputs.put("limit_evalue_accept", "1e-8");
                userInputs.put("ignore_method2", "false");
            }
            runCaseStudy(userInputs, requiredFiles, taxonomyID, transytDirectory);
        }
    }

    public static void runCaseStudy(HashMap<String, String> userInputs, List<File> requiredFiles, long taxonomyID, String transytDirectory) {
        String url = "https://transyt.bio.di.uminho.pt//";
        HandlingRequestsAndRetrievalsTransyt post = new HandlingRequestsAndRetrievalsTransyt(requiredFiles, taxonomyID, url);
        String submissionID;
        try {
            submissionID = post.postFiles(userInputs);

            if (submissionID != null) {

                try {
                    System.out.println("SubmissionID attributed: " + submissionID);
                    int responseCode = -1;


                    System.out.println("files submitted, waiting for results...");

                    while (responseCode != 200) {

                        responseCode = post.getStatus(submissionID);

                        if (responseCode == -1) {
                            System.out.println("Error!");
                            System.exit(1);
                        } else if (responseCode == 503) {
                            System.out.println("The server cannot handle the submission due to capacity overload. Please try again later!");
                            System.exit(1);
                        } else if (responseCode == 500) {
                            System.out.println("Something went wrong while processing the request, please try again");
                            System.exit(1);
                        } else if (responseCode == 400) {
                            System.out.println("The submitted files are fewer than expected");
                            System.exit(1);
                        }
                        TimeUnit.SECONDS.sleep(3);
                    }

                    System.out.println("downloading TranSyT results");

                    post.downloadFile(submissionID, transytDirectory.concat("/results.zip"));

                    System.out.println("verifying...");

                    String transytResultsFile = transytDirectory.concat("results/");

                    FileUtils.extractZipFile(transytDirectory.concat("/results.zip"), transytResultsFile);

                } catch (Exception e) {
                    e.printStackTrace();
                }
            } else
                System.out.println("No dockerID attributed!");
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Error submitting files");
        }
    }
}




