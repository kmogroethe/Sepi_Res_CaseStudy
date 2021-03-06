#!/usr/bin/python3
###############################################################################
# Purpose: Variant Call for Sepi project
# Author: Nick Brazeau
#Given: Bam
#Return: VCF
# Note, this project has been optimized for GATK 3.8 (older version as 4.0 is now available)
###############################################################################


####### Working Directory and Project Specifics ############
workdir: '/pine/scr/n/f/nfb/Projects/Sepi_Res_CaseStudy/'
readdir = '/pine/scr/n/f/nfb/Projects/Sepi_Res_CaseStudy/wgs_pe_improved/aln/merged/'
SAMPLES, = glob_wildcards(readdir + '{sample}.bam')


################   REFERENCE    ##############
REF = '/proj/ideel/resources/genomes/Sepidermidis/genomes/CORE_GCF_000007645.1_ASM764v1_genomic.fasta'
GFF = '/proj/ideel/resources/genomes/Sepidermidis/info/gff/GCF_000007645.1_ASM764v1_genomic.gff'


TMPDIR = '/pine/scr/n/f/nfb/PicardandGATKscratch'
ProjName = 'Sepi_Res_CaseStudy'
##########################################################################################

#############################
#######  RULE ALL  ##########
#############################


rule all:
#	input: expand('variants/{sample}_HaploCaller.raw.g.vcf', sample = SAMPLES)
#	input: expand('variants/{ProjName}_HaploCaller_joint.raw.vcf', ProjName = ProjName)
	input: expand('variants/{ProjName}_HaploCaller_joint.ann.vcf', ProjName = ProjName)



##########################################################################################
##########################################################################################
#########################           Variant Annotation             #######################
##########################################################################################
##########################################################################################
rule Annotate_POP_SNPeffvariants:
	input: vcf = 'variants/{ProjName}_HaploCaller_joint.pass.vcf', snpeff='variants/{ProjName}_HaploCaller_joint.snpEff.vcf'
	output: 'variants/{ProjName}_HaploCaller_joint.ann.vcf'
	shell: 'java -jar /nas/longleaf/apps/gatk/3.8-0/GenomeAnalysisTK.jar -T VariantAnnotator \
		-R {REF} \
		-A SnpEff \
		-V {input.vcf} \
		--snpEffFile {input.snpeff} \
		-o {output}'

rule snpEff_Pop_variants:
	input: vcf = 'variants/{ProjName}_HaploCaller_joint.pass.vcf'
	output: 'variants/{ProjName}_HaploCaller_joint.snpEff.vcf'
	shell: 'snpEff -v -o gatk Staphylococcus_epidermidis_atcc_12228 {input.vcf} > {output}'

rule select_variants:
	input: 'variants/{ProjName}_HaploCaller_joint.qual.vcf'
	output: 'variants/{ProjName}_HaploCaller_joint.pass.vcf'
	shell: 'gatk --java-options "-Xmx4g -Xms4g" SelectVariants \
		-R {REF} -V {input} --output {output} \
		-select "vc.isNotFiltered()"'

rule filter_variants:
	input: 'variants/{ProjName}_HaploCaller_joint.raw.vcf'
	output: 'variants/{ProjName}_HaploCaller_joint.qual.vcf'
	shell: 'gatk --java-options "-Xmx4g -Xms4g" VariantFiltration \
		-R {REF} \
		-V {input} \
		--filter-expression "MQ < 55.0" \
		--filter-name "MQ" \
		--filter-expression "SOR > 2.0" \
		--filter-name "SOR" \
		--output {output}'


rule genotype_GVCFs:
	input: 'variants/{ProjName}_HaploCaller_joint.combined.g.vcf'
	output: 'variants/{ProjName}_HaploCaller_joint.raw.vcf'
	shell: 'gatk --java-options "-Xmx4g -Xms4g" GenotypeGVCFs \
		    -R {REF} \
		    --variant {input} \
		    --output {output}'


rule combine_gvcfs:
	input: '/proj/ideel/meshnick/users/NickB/Projects/Sepi_Res_CaseStudy/gatk/Sepi_gvcfs.list'
	output: 'variants/{ProjName}_HaploCaller_joint.combined.g.vcf'
	shell: 'gatk --java-options "-Xmx4g -Xms4g" CombineGVCFs \
		    -R {REF} \
		    --variant {input} \
		    --output {output}'


rule haplotype_caller:
	input: readdir + '{sample}.bam',
	output: 'variants/{sample}_HaploCaller.raw.g.vcf'
	shell: 'gatk --java-options "-Xmx4g -Xms4g" HaplotypeCaller \
		-R {REF} -I {input} \
		-ploidy 1 \
		-ERC GVCF \
		--output {output} '
