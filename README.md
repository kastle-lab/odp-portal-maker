# odp-portal-maker
This repo houses:
* the scripts to create the ODP portal
* the scripts to generate a MODL index for the ODP portal
* a template for WOP website instances

## Workflow
* Ingest the ODP Portal dump
* Run through `pandoc` to convert to MarkDown
* Create a sane directory structure
  * each directory should have the pattern's OWL file, schema diagram, and pattern page.

## Deliverables
* A collection of hyperlinked MarkDown files that represents the ODP Portal
* A MODL inxdex of the ODP Portal
* Create a list of pattern contributors
