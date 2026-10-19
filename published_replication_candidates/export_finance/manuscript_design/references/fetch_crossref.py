import json,pathlib,urllib.request,urllib.parse,time
p=pathlib.Path(__file__).resolve().parent
dois=['10.1038/s41467-025-55981-0','10.1007/s10584-025-03881-z','10.1111/1758-5899.13121','10.1080/09692290.2023.2272845','10.1111/1758-5899.12894','10.1016/j.joule.2022.05.003','10.1111/j.1758-5899.2011.00132.x','10.1007/s11558-025-09613-3','10.1016/j.erss.2023.103127','10.1016/j.worlddev.2024.106623','10.1016/j.eneco.2024.107455','10.1080/14693062.2022.2080634','10.1080/17565529.2017.1410087','10.1038/s41560-024-01606-7','10.1038/s41467-021-24305-3','10.1016/j.isci.2023.106945','10.1088/2516-1083/ac7936','10.1016/j.eneco.2017.11.006','10.1088/1748-9326/ace6c1','10.1038/s41560-018-0280-3','10.1080/01621459.1955.10501299','10.2307/145818','10.1371/journal.pone.0321874','10.1186/s12992-026-01224-w']
a=[]
for doi in dois:
 u='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
 try:
  d=json.load(urllib.request.urlopen(u,timeout=25))['message'];a.append({'doi':doi,'url':u,'metadata':d});print(doi,d.get('title'),flush=True)
 except Exception as e:a.append({'doi':doi,'url':u,'error':str(e)});print(doi,e,flush=True)
 (p/'crossref_verified_metadata.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));time.sleep(1.5)
