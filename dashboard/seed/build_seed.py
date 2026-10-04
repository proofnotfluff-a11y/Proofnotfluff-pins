import json
days = {
 "2026-09-27": dict(etsyVisits=0, listed=2, note="#1 and #2 went live"),
 "2026-09-28": dict(etsyVisits=1),
 "2026-09-29": dict(etsyVisits=5, listed=6, note="#3 to #8 live (listed between Sep 27 and 29)"),
 "2026-09-30": dict(etsyVisits=1),
 "2026-10-01": dict(etsyVisits=3, listed=2, pins=5, note="#9 and #10 live; first pins"),
 "2026-10-02": dict(etsyVisits=3, listed=2, pins=7, shorts=4, posts=1, note="#11 and #12 live; first Shorts"),
 "2026-10-03": dict(etsyVisits=1, listed=1, pins=8, shorts=3, posts=2, note="#13 Service Pricing Calculator live; first X post"),
 "2026-10-04": dict(etsyVisits=1, pins=3, shorts=1, note="Partial: Etsy stats lag about 5 hours"),
}
for d,v in days.items():
    for k in ["etsyVisits","listed","pins","shorts","posts","favorites","orders","revenue","reviews"]:
        v.setdefault(k,0)
    v["date"]=d
shorts = [
 ("svc-40-hourly","A $40 hourly rate pays you about $20","2026-10-03",1010,"13","https://youtube.com/shorts/u6xIhZwKRfg"),
 ("svc-20-mile","A 20-mile round trip adds $52 to the job","2026-10-04",116,"13","https://youtube.com/shorts/IUCBAnmd2QQ"),
 ("ship-dim-weight","Shrink the box 2 inches, pay $11.57 instead of $21.15","2026-10-02",57,"7","https://youtube.com/shorts/8tjDxYjwk0E"),
 ("binder-401k","Your will does not control your 401(k)","2026-10-03",48,"11","https://youtube.com/shorts/MIacRyOSAYA"),
 ("str-fee","Airbnb 15.5% host fee: what a $200 night really pays you","2026-10-02",24,"9","https://www.youtube.com/channel/UCxSPVQhZhYoR1yKFRrWgIew/shorts"),
 ("star-90s","STAR interview answer: keep it to 90 seconds","2026-10-03",12,"1","https://youtube.com/shorts/lPftlhksk70"),
 ("reorder-112","When to reorder inventory: the 112-unit answer","2026-10-02",10,"6","https://www.youtube.com/channel/UCxSPVQhZhYoR1yKFRrWgIew/shorts"),
 ("booth-51","A $150 booth fee takes 51 pieces to break even","2026-10-02",3,"12","https://youtube.com/shorts/2DXKkKAjnow"),
]
agents = [
 dict(id="shop-run",order=1,name="Daily shop run",schedule="6:50 am daily",where="Todd's PC",role="Weekday playbook, Etsy stats, comments digest, listing fixes",lastRun="Sun Oct 4, 6:50 am",lastStatus="ok",lastNote="No pins on Sunday by design; 0 new comments; #8 category confirmed; flagged two LinkedIn posts with invented people."),
 dict(id="morning-promote",order=2,name="Morning promote",schedule="7:05 am daily",where="Cloud",role="3 pins and 1 Short",lastRun="Sun Oct 4, 7:05 am",lastStatus="ok",lastNote="Pins for #13, #12, #11 and the 20-mile Short (116 views so far). Replaced one pin whose figure Apple's docs do not state."),
 dict(id="factory",order=3,name="Product factory",schedule="8:20 am daily",where="Todd's PC",role="Researches, builds, gates and lists one new product a day",lastRun="",lastStatus="",lastNote="First run with the new saturation check is today."),
 dict(id="afternoon-promote",order=4,name="Afternoon promote",schedule="4:10 pm daily",where="Cloud",role="2 pins and 1 Short",lastRun="Sat Oct 3, 4:10 pm",lastStatus="ok",lastNote="Pins for #13 and #8 and the $40 hourly rate Short, now at 1,010 views."),
]
stores = [
 dict(id="etsy",order=1,name="Etsy",status="live",detail="13 listings, 30% sale through Oct 28. Only digital sales platform today.",url="https://www.etsy.com/shop/ProofNotFluff"),
 dict(id="instagram",order=2,name="Instagram",status="setup",detail="Todd is setting it up today. Reels and posts with the Etsy link in bio; Instagram Shop can't sell downloads."),
 dict(id="kdp",order=3,name="Amazon KDP",status="planned",detail="Paperback editions of #11 and #8 are next in the print queue."),
 dict(id="payhip",order=4,name="Payhip or Gumroad",status="held",detail="Held until social sends 100+ clicks a month off Etsy."),
]
quests = [
 dict(id="instagram-setup",order=1,owner="todd",title="Set up the Instagram business account",detail="Then connect it in Zapier so the crew can post Reels.",xp=50),
 dict(id="youtube-link",order=2,owner="todd",title="Add the Etsy shop link to the YouTube channel",detail="YouTube Studio, Customization: add etsy.com/shop/ProofNotFluff as a channel link. Shorts description links don't click.",xp=40),
 dict(id="decide-1",order=3,owner="todd",title="Decide on #1, the AI prompt pack",detail="Etsy's Creativity Standards say prompt bundles aren't seller-designed. Reply \"1 retire\" or ask for a repackage.",xp=40),
 dict(id="pinterest-business",order=4,owner="todd",title="Switch Pinterest to a free business account",detail="Unlocks analytics, then claim the Etsy shop.",xp=30),
 dict(id="production-partners",order=5,owner="todd",title="Remove the old production partners",detail="Etsy shop settings: the China craft partner and print shop from the old shop still show on the shop page.",xp=25),
 dict(id="linkedin-posts",order=6,owner="todd",title="Fix the two LinkedIn posts with invented people",detail="\"A host I know\" (Oct 2) and \"a shop owner I worked with\" (Oct 3). Delete or rewrite as worked examples.",xp=25),
 dict(id="factory-computer",order=7,owner="todd",title="Turn on \"Require this computer\" for the factory task",detail="So the 8:20 am factory always runs where Chrome and Etsy are signed in.",xp=20),
 dict(id="buyer-note",order=8,owner="todd",title="Replace the old Mythic Atlas note to buyers",detail="Etsy Settings, Info & Appearance. The new text was sent Oct 2.",xp=20),
 dict(id="crew-trade-editions",order=20,owner="crew",title="Ship the service pricing trade editions",detail="One per factory day, each must pass the saturation check first.",xp=0),
 dict(id="crew-listing-lab",order=21,owner="crew",title="Run the first Listing Lab test",detail="Monday reviews: one change per listing, 14-day windows.",xp=0),
 dict(id="crew-kdp",order=22,owner="crew",title="Publish the first KDP paperback",detail="Print edition of #11, the emergency binder.",xp=0),
]
meta = dict(
 statsAsOf="Oct 4, 3:40 am (read 8:45 am)",
 shortsAsOf="Oct 4, 8:50 am",
 listingsLive=13,
 sourcesWindow="Sep 5 to Oct 4, Etsy Stats",
 sources=[
  dict(key="direct",label="Direct and referral",visits=6),
  dict(key="etsy-pages",label="Etsy app and pages",visits=6),
  dict(key="search",label="Etsy search",visits=3),
  dict(key="marketing",label="Etsy marketing and SEO",visits=1),
  dict(key="pinterest",label="Pinterest",visits=1),
  dict(key="youtube",label="YouTube Shorts",visits=0,note="1,280 Short views, 0 visits: description links don't click. Fixed Oct 4."),
  dict(key="linkedin-x",label="LinkedIn and X",visits=0),
 ],
 funnel=[dict(label="Listing views",value=20),dict(label="Favorites",value=0),dict(label="Orders",value=0)],
 mainQuest=dict(title="Land the first sale",blockers=[
  dict(status="open",text="Etsy search sent 3 visits in 30 days. New listings have no sales, favorites or reviews to rank on."),
  dict(status="open",text="Page 1 is crowded with near-identical calculators from other new shops."),
  dict(status="fixed",text="Shorts pointed to a link that can't be tapped. Every Short now shows etsy.com/shop/ProofNotFluff."),
  dict(status="watch",text="Shop reviews are all from the 2023 mushroom shop. The first real review fixes that."),
 ]),
)
log = {
 "2026-10-01": [dict(t="",agent="Setup",text="First pins published for #9 and #5."),dict(t="2:33 pm",agent="Shop run",text="3 more pins (#9, #8, #2); two new boards.")],
 "2026-10-02": [dict(t="6:50 am",agent="Shop run",text="Pins for #6, #9, #10."),dict(t="10:41 am",agent="Setup",text="First two Shorts live; afternoon promote task created."),dict(t="12:22 pm",agent="Afternoon promote",text="Pins for #7 and #1; shipping Short."),dict(t="2:20 pm",agent="Todd",text="#11 and #12 found live, listed by Todd."),dict(t="4:10 pm",agent="Afternoon promote",text="Pins for #12 and #11; booth fee Short.")],
 "2026-10-03": [dict(t="7:40 am",agent="Shop run",text="Pins for #11, #12, #10 and the 401(k) Short."),dict(t="7:55 am",agent="Setup",text="X connected; first X post live."),dict(t="9:55 am",agent="Morning promote",text="Pins for #1, #11, #12 and the STAR Short."),dict(t="3:15 pm",agent="Factory",text="Built, gated and listed #13 Service Pricing Calculator.",xp=50),dict(t="3:45 pm",agent="Audit",text="All 13 prices verified; #13 to $6.99 founding; offers off."),dict(t="4:10 pm",agent="Afternoon promote",text="Pins for #13 and #8; $40 hourly Short (now 1,010 views)."),dict(t="5:30 pm",agent="Audit",text="Categories fixed on 6 listings."),dict(t="7:55 pm",agent="Audit",text="Etsy's title suggestions applied to 9 listings.")],
 "2026-10-04": [dict(t="6:50 am",agent="Shop run",text="Sunday: no pins by design; 0 new comments."),dict(t="7:05 am",agent="Morning promote",text="Pins for #13, #12, #11 and the 20-mile Short."),dict(t="8:55 am",agent="Audit",text="Shop audit: Shorts link leak found and fixed; saturation check added to the factory.")],
}
writes=[]
for d,v in days.items(): writes.append(dict(op="set",collection="days",doc_id=d,data=v))
for i,t,dt,vw,p,u in shorts: writes.append(dict(op="set",collection="shorts",doc_id=i,data=dict(title=t,date=dt,views=vw,product=p,url=u)))
for a in agents: writes.append(dict(op="set",collection="agents",doc_id=a.pop("id"),data=a))
for s in stores: writes.append(dict(op="set",collection="stores",doc_id=s.pop("id"),data=s))
for q in quests: q.update(done=False); writes.append(dict(op="set",collection="quests",doc_id=q.pop("id"),data=q))
for d,e in log.items(): writes.append(dict(op="set",collection="log",doc_id=d,data=dict(entries=e)))
writes.append(dict(op="set",collection="meta",doc_id="shop",data=meta))
json.dump(writes,open("seed/writes.json","w"),indent=1)
print(len(writes),"writes")
