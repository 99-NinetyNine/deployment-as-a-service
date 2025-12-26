user provides a github link via command line
user provides a domain name via command line

github has either docker compoe or Dockerile in its file 

if docker file 
only one service 

if docker compose more than one service 

since docker compose can have service name for which the domain name is providede make some rule 
since redis is not servied via domain name so its relaxed 

but api needs so 
api_subdomain_domain_name the underscored is acted as a . 

and if its a single docker file it shold tell whether it needs a domain or not in the 2nd command in step 2. 
for docker compose as it can have more than one api so ask for domain name until user types stop


now that is deployment as a service. 


also the main ngin is alsays the service that is setup initially. its dockerrized. 
for each sites it needs to serve our system auto generates what it needs. and if maual modifucation needed? then that is 
also allowed. 

so nginx have to serve many many files. 

and moreoover we need to setup the letsencrypt for the domain name ssl generation and verification.
make this also a sutomated process. 

haha. 

now setting up these would make the deployment very easy right?



also if others command lines needed add them too. haha very nice system right?


the letsc cencypt, certbot, all are dcokereized. 
