

let players = undefined;
let p2id = undefined;

export async function players_load() {
  const xres = await fetch('players2.json');
  players = await xres.json();
  p2id = {};
  for (const [key, value] of Object.entries(players)) {
    p2id[value.data.names.international] = key;
  }
}

export function player_get( pid ) {
  if(players === undefined) {
    return undefined;
  }
  return players[pid];
}
export function player_get_name( name ) {
  if(players === undefined || p2id === undefined ) {
    return undefined;
  }
  return players(p2id[name]);
}
export function player_name_to_id( name ) {
  if(p2id === undefined) {
    return undefined;
  }
  return p2id[name];
}


export function player_keys() {
  if(players === undefined) {
    return undefined;
  }
  return Object.keys( players )
}
  

export function xcolor( pid ) {
  var style = players[pid]['data']["name-style"];
  //console.log(style);
  if(style.style == "gradient") {
    return style['color-from']['light'];
  }
  if(style.style == 'solid') {
    return style['color']['light'];
  }
  console.log('No color style found',pid);
  return 'black';
}

export function name(id) {
  return players[id].data.names.international;
}

// Determine the mapping from names to id
$: {
  if(players !== undefined) {
    //console.log("BUILDING NAME MAPPING");
  }
}
