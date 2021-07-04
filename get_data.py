#!/usr/bin/env python3

import sys
import json
import time
import subprocess


cats = {
    "any": { "id": "vdoq4xvk", "output_file": "all.json", "output_file2": "all2.json", },
    "100": { "id": "xk9jv4gd", "output_file": "100.json", "output_file2": "1002.json", },
    'amq': { "id": "n2yj3r82", "output_file": "amq.json", "output_file2": "amq2.json", },
    "as":  { "id": "wkpqmw8d", "output_file": "as.json",  "output_file2": "as2.json",  },
    "ad":  { "id": "9d8jgv7k", "output_file": "ad.json",  "output_file2": "ad2.json", }
}

def get_next_link( v ) :
    links = v['pagination']['links']
    URL = None
    for link in links:
        if link['rel'] == 'next':
            return link['uri']
    return None

def get_player_ids_from_runs( out ):
    ids = []
    for run in out:
        pids = [p['id'] for p in run['players'] if 'id' in p]
        ids.extend(pids)
    return list(set(sorted(ids)))

def get_url( URL ):
    p = subprocess.run(['curl', URL], capture_output = True)
    return json.loads( p.stdout )

def get_runs_at_offset( category, offset ):
    URL="https://www.speedrun.com/api/v1/runs?category={}&orderby=submitted&direction=asc&offset={}".format( category, offset )
    return get_url( URL )


def get_all_runs( category, offset = 0 ):
    out = []
    URL="https://www.speedrun.com/api/v1/runs?category={}&orderby=submitted&direction=asc&offset={}".format( category, offset  )
    n=0
    while URL is not None:
        v = get_url( URL )
        out.extend( v['data'] )
        URL = get_next_link( v )
        print("{:5} {}".format(len(out), URL))
        time.sleep(1)
    return out

def load_runs( filename ):
    chunk = 20
    runs = json.load(open(filename,'r'))
    category = runs[0]['category']
    n = len(runs)
    n20 = (n // chunk) * chunk
    tmp = get_runs_at_offset(category, n20)
    if tmp['data'][0]['id'] == runs[n20]['id']: # Check if first id in downloaded data matches the same in the existing data
        print("   Last ID matches, just update runs", len(runs))
        runs = runs[:n20]  # Truncate runs at beginning of chunk
        runs.extend(tmp['data']) # Add "new" runs
        URL = get_next_link( tmp )
        if URL is not None:
            print(" ... Last chunk has more runs, get 'em")
            r = get_all_runs( category, offset = n20 + chunk )
            runs.extend( r )
        return runs
    else :
        raise ValueError("IDs do not match")
    return runs

def get_all_players( ids ):
    pid = {}
    for xid in ids:
        #print(id)
        url = "https://www.speedrun.com/api/v1/users/{}".format(xid)
        #print(url)
        args = ['curl', '--silent', url]
        p = subprocess.run(args, stdout=subprocess.PIPE)
        v = json.loads(p.stdout.decode())
        pid[xid] = v
        print("ID {}".format(xid))
        time.sleep(1)
    return pid

def update_players_list( runs, players_file = 'players.json'):
    ids = get_player_ids_from_runs( runs )

    players = json.load(open(players_file,'r'))
    new_ids = [ key for key in ids if key not in players ]
    if len(new_ids) > 0:
        players_new = get_all_players( new_ids )

        players.update( players_new )
        with open(players_file, 'w') as fp:
            json.dump( players, fp )


if __name__ == '__main__':
    players_file = "players.json"
    players_file2 = "players2.json"

    if len(sys.argv) < 2:
        print("Usage: get_data.py -a -p -r -f category")
        print("    -a  Get all runs (starts over)")
        print("    -f  Filter runs and players")
        print("    -u  Update runs")
        print("    -p  Update players")
        print("    Ex: next.py -u -p -f all # Update all categories ")
        print("        next.py -a -p -f all # Get all categories ")
        sys.exit(0)
    cat = sys.argv[-1]
    if cat not in cats and cat != "all":
        print("Please specify a category")
        for key in cats.keys() :
            print("  ", key)
        print("   all")
        sys.exit(-1)
    if cat == "all":
        categories = list(cats.keys())
    else:
        categories = [ cat ]

    get_all = any([arg == '-a' for arg in sys.argv[1:]])
    update_players = any([arg == '-p' for arg in sys.argv[1:]])
    update_runs    = any([arg == '-u' for arg in sys.argv[1:]])
    filter_data    = any([arg == '-f' for arg in sys.argv[1:]])

    runs = []
    if get_all:
        for cat in categories:
            c = cats[cat]
            runs = get_all_runs( c['id'] )
            out = c['output_file']
            with open(out, 'w') as fp:
                json.dump( runs, fp )
            if update_players:
                update_players_list( runs )

    if update_runs:
        for cat in categories:
            print("Updating category:", cat)
            c = cats[cat]
            out = c['output_file']
            runs = load_runs( out )
            with open(out, 'w') as fp:
                json.dump( runs, fp )
            if update_players:
                print("   Updating players ...")
                update_players_list( runs )

    if filter_data:
        for cat in categories:
            c = cats[cat]
            out = c['output_file']
            out2 = c['output_file2']
            runs = json.load(open(out,'r'))
            rout = []
            # Remove extra field we are not using 
            for r in runs:
                r2 = {}
                if len(r['players']) == 0:
                    continue
                if 'id' not in r['players'][0]:
                    continue
                for k in ['id','weblink','submitted']:
                    r2[k] = r[k]
                r2['status'] = { 'status': r['status']['status'] }
                r2['times'] = {'primary_t': r['times']['primary_t'] }
                r2['players'] = [ {'id': r['players'][0]['id'] } ]
                r2['values'] = r['values']
                rout.append(r2)
            json.dump( rout, open(out2,'w'))

        # Players file Remove extra fields we 
        players = json.load(open(players_file, 'r'))
        pout = {}
        for k,v in players.items():
            pout[k] = {
                'data': {
                    'weblink': v['data']['weblink'],
                    'names': v['data']['names'],
                    'name-style': v['data']['name-style'],
                }
            }
        json.dump( pout, open(players_file2,'w'))


