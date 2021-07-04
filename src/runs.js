
let runs = []; // Usable runs
let runs0 = []; // Original runs including rejected runs

let vars = undefined;
let vars0 = undefined;

export async function runs_load( input_file ) {
  const res = await fetch( input_file );
  runs0 = await res.json();
  runs = runs0.filter(r => verified(r));
}
export async function variables_load( input_file ) {
  // https://www.speedrun.com/api/v1/categories/n2yj3r82/variables
  const res = await fetch ( input_file );
  vars0 = await res.json();
  vars = {};
  for(var key in vars0.data) {
    let v = vars0.data[key];
    let name = v.name;
    let id = v.id;
    let tmp = {id: id};
    for(var k in v.values.values) {
      let label = v.values.values[k].label;
      tmp[label] = k;
    }
    vars[name] = tmp
  }
}

function verified(run) {
  return run['status']['status'] === 'verified'
}

export function runs_get( f  ) {
  if(f === undefined) {
    return runs;
  } else{
    return runs_filt( f );
  }
}

export function runs_filt( kv ) {
  return runs.filter(run => {
    for(const key in kv) {
      if(run.values[key] !== kv[key]) {
        return false;
      }
    }
    return true;
  });
}

function obj_get(obj, key, value, return_key) {
  for(let k in obj) {
    if(obj[k][key] === value) {
      if(return_key) {
        return k;
      }
      return obj[k];
    }
  }
  return undefined;
}

async function get_vars(x) {
  return new Promise(function(resolve, reject) {
    if(vars === undefined) {
      setTimeout( function() { resolve( get_vars(x) ); }, 300);
    } else {
      resolve( vars );
    }
  });
}

export async function var_get( var_name, value_name) {
  let svar = await get_vars(var_name);
  if(!(var_name in svar)) {
    console.log(var_name, value_name);
    return undefined;
  }
  //console.log(svar)
  let v = svar[var_name];
  let id = v.id;
  let val = v[value_name];
  let out = {};
  out[id] = val;
  return out;
}




