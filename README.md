Running TranSyT

TranSyT can be accessed at www.transyt.bio.di.uminho.pt or it can be runned as a maven project.

The inputs required to run TranSyT at the website are available in the folder "example" of this repository. The "protein.faa" file is the genome of _Escherichia coli K-12_ (TaxonomyID 83333). The folder contains one list of metabolites with the whole KEGG Compound database ("kegg_compounds.txt").



To run TranSyT as a maven project, proceed as follows:

1. Clone this repository;
2. Open the folder "transyt_app" as a maven project with your IDE, and download the required sources/dependencies.
3. Run the "App" (src.main.java.pt.uminho.ceb.biosystems.merlin.transyt_app.App) as main class. Here you can configure how you want to run the tool, 
including the path to the genome/compounds files, taxonomy ID, and TranSyT parameters.


