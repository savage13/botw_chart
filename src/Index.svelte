<script>

  import luxon from '../node_modules/luxon';
  import { Chart, LineController, LineElement, PointElement, LinearScale, Title, TimeScale, Tooltip, Legend } from '../node_modules/chart.js';
	import { onMount } from 'svelte';
  import 'chartjs-adapter-luxon';
  import zoomPlugin from 'chartjs-plugin-zoom';

  import { xcolor, name, players_load, player_keys, player_name_to_id, player_get } from './players.js';

  import { runs_load, variables_load, var_get, runs_get, runs_filt } from './runs.js';

  Chart.register(LineController, LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend);
  Chart.register(zoomPlugin);

  var DateTime = luxon.DateTime;

  function seconds(x) {
    return 1000 * x;
  }
  function minutes(x) {
    return seconds(60 * x);
  }
  function hours(x) {
    return minutes(60 * x);
  }

  //console.log(window.location.search);
  let params = new URLSearchParams( window.location.search );
  let category = params.get('cat');

  let input_file = undefined;
  let min_y_limit = 0.0;
  let max_y_limit = 1.0;
  let y_time_unit = "";

  var xids = []; // Hold meta data about runs and players

  //let players = undefined;
  //let p2id = undefined;
  var chart = undefined;
  let push_data = true;
  let title = "";
  let var_file = "";

  let original_mode = "013vo7xl";
  let extended_mode = "rqv4ko6q";
  let normal_mode = '9qjw2z01';
  let master_mode = 'jq6yv4n1';
  let strict_off  = '0q5ykk2l';
  let strict_on   = '4lxr334l';
  let game_mode   = normal_mode; // Normal or Master
  let dlc_mode    = "";          // DLC or No DLC (Extended or Original)
  let strict_mode = "";          // Restricted or No Restrictions
  let amiibo_on   = true;        // Both on and off can be shown at the same time
  let amiibo_off  = true;

  function set_category() {
    if(category == "any") {
      //console.log("SETTING CATEGORY to ANY");
      input_file = "all2.json";
      min_y_limit = minutes(20);
      max_y_limit = minutes(60);
      y_time_unit = "minute";
      title = "Any%";
      var_file = "any_var.json";
    } else if(category == "100") {
      //console.log("SETTING CATEGORY to 100");
      input_file = "1002.json";
      min_y_limit = hours( 15 );
      max_y_limit = hours( 45 );
      y_time_unit = "hour";
      title = "100%";
      var_file = "100_var.json";
      game_mode = "";
      strict_mode = "";
      dlc_mode  = original_mode;
    } else if(category == "amq") {
      //console.log("SETTING CATEGORY to 100");
      input_file = "amq2.json";
      min_y_limit = hours( 2 );
      max_y_limit = hours( 6 );
      y_time_unit = "minute";
      title = "All Main Quests"
      var_file = "amq_var.json";
      game_mode = "";
      dlc_mode  = original_mode;
      strict_mode = strict_off;
    } else if(category == "as") {
      //console.log("SETTING CATEGORY to 100");
      input_file = "as2.json"
      min_y_limit = hours( 4 );
      max_y_limit = hours( 16 );
      y_time_unit = "minutes";
      title = "All Shrines";
      var_file = "as_var.json";
      game_mode = "";
      dlc_mode  = original_mode;
      strict_mode = strict_off;
    } else if(category == "ad") {
      //console.log("SETTING CATEGORY to 100");
      input_file = "ad2.json";
      min_y_limit = hours( 1.5 );
      max_y_limit = hours( 3 );
      y_time_unit = "minutes";
      title = "All Dungeons";
      var_file = "ad_var.json";
      game_mode = "";
      dlc_mode  = original_mode;
      strict_mode = "";
    } else {
      category = "any";
      set_category();
    }
  }

  set_category();

  async function create_chart() {
    let ele = document.getElementById("chart");
    if(ele != null) {
      chart = new Chart(ele, config);
    }
  }

  onMount(async () => {
    await create_chart();
    await players_load();
    await runs_load( input_file );
    await variables_load( var_file );
    //charty_update();
    xids_init();
	});


  function date_from_string(x) {
    return DateTime.fromISO(x).toUTC();
  }

  function link(href, txt, new_window=false) {
    var v = document.createElement("a");
    v.setAttribute('href', href);
    v.classList.add('redlink');
    if(new_window) {
      v.setAttribute('target','_blank');
    }
    v.appendChild(document.createTextNode(txt));
    return v;
  }

  let last_touch_start = undefined;

  function now() {
    let now = new Date();
    return now.getTime();
  }
  var data = { datasets: [] };

  let popups = [];
  let config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onResize: function(c, size) {
        //console.log(c,size);
      },
      onHover: (e) => {
        if(e.native.type == "touchstart") {
          // Identify if a "touch" started, tooltips only get shown if the
          //   event that creates a tooltip does not immediately follow
          //   the touch start event
          last_touch_start = now();
        }
      },
      onClick: (e) => {
        const pts = chart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
        if(pts.length) {
          const p = pts[0];
          let pt = p.element['$context'].raw;
          let id = pt.id;
          let run_id = pt.run_id;
          let n = name(id);
          var div = document.querySelector(`#${run_id}`);
          //console.log(div);
          if(div !== null) {
            //console.log(`Popup already exists: ${run_id}`);
            return;
          }
          let t = s2hms(pt.t);
          var div = create_popup_element( undefined  );
          let video = pt.url;
          // Popup Content
          let txt = document.createElement("div");
          txt.appendChild( document.createTextNode(`${n}: ${t} - `) );
          txt.appendChild( link(video, 'video', true));
          txt.appendChild(document.createTextNode(' - '));
          let active = is_active( n );
          let v = link('#', (active) ? 'hide' : 'show all');
          v.onclick = function(ev) {
            if(is_active(n)) {
              remove_active( n );
            } else {
              add_active( n );
            }
            div.remove();
            popups = popups.filter(e => e.id !== n);
          }
          txt.appendChild( v );
          let close = document.createElement('span');
          close.style.cursor = 'pointer';
          close.style.paddingLeft = '3px';
          close.innerHTML = "x";
          close.onclick = function(ev) {
            div.remove();
            popups = popups.filter(e => e.id !== n);
          }
          txt.appendChild(close);

          // Create the popup with the content
          create_popup({
            html: txt,
            caretX: p.element.x,
            caretY: p.element.y,
            options: {
              padding: 6
            }
          }, div);
          let parent = document.querySelector('#chart_parent');
          parent.appendChild( div );
          div.style.transform = 'translate(7px,-50%)';
          div.style.zIndex = "2";
          div.style.pointerEvents = 'auto';
          div.setAttribute('id', run_id);
          popups.push({div: div, datasetIndex: p.datasetIndex, index: p.index, id: n });
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 7,
            filter: function(legendItem, chartData) {
              if(legendItem.text == "WR" || legendItem.text == "all runs") {
                return true;
              }
              if(category == "any") {
                if(!amiibo_off && legendItem.text.includes("(no amiibo)")) {
                  return false;
                }
                if(!amiibo_on && !legendItem.text.includes("(no amiibo)")) {
                  return false;
                }
              }
              return true;
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        title: {
          display: false,
          text: 'BotW Any%'
        },
        tooltip: {
          enabled: false,
          position: 'nearest',
          external: external_tooltip,
          bodyFont: {
            family: 'Arial',
            size: 8,
          },
          callbacks: {
            title: function(context) {
              return undefined;
            },
            label: function(context) {
              var id = context.raw.id;
              var t = s2hms(context.raw.t);
              var x = context.raw.x.toFormat('yyyy-LL-dd HH:mm');
              var n = name(id);
              var url = context.raw.url;
              //var t = context.formattedValue;
              var tag = document.getElementById("tmp");
              var aa = (context.raw.amiibo) ? "amiibo" : "no amiibo";
              return `${n}: ${t} ${x} ${aa}`;
            },
          },
        },
        zoom: {
          limits: {
            y: {
              min: 0,
              //max: max_y_limit
            },
            x: {
              min: date_from_string("2015-01-01T00:00:00").toMillis(),
              max: date_from_string("2023-01-01T00:00:00").toMillis(),
            },
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05,
            },
            pinch: {
              enabled: true,
            },
            mode: 'xy',

          },
          pan: {
            enabled: true,
            threshold: 1,
            model: 'xy',
            onPan: panning,
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          adapters: {
            date: {
                zone: 'UTC',
            }
          },
          time: {
            tooltipFormat: 'yyyy-LL-dd TTT',
            unit: 'month',
            displayFormats: {
              month: 'LLL yyyy'
            },
          },
        },
        y: {
          type: 'time',
          //min: DateTime.fromMillis(25*60*1000),
          min: min_y_limit,
          max: max_y_limit,
          suggestedMax: max_y_limit,
          adapters: {
            date: {
              zone: 'UTC',
            }
          },
          ticks: {
            callback: function(value, index, values) {
              return s2hms(values[index].value/ 1000.0);
            }
          },
          time: {
            unit: y_time_unit,
            tooltipFormat: 'mm:ss.SSS',
            displayFormats: {
              minute: "mm:ss",
              hour: "hh:mm:ss",
            },
            stepSize: 5,
          },
        }
      }
    }
  };

  function panning(c) {
    const {offsetLeft: positionX, offsetTop: positionY} = c.chart.canvas;
    popups.forEach(p => {
      var meta = c.chart.getDatasetMeta(p.datasetIndex);
      if(meta.data && meta.data.length > 0) {
        let div = p.div;
        let pt = meta.data[p.index];
        div.style.left = positionX + pt.x + "px";
        div.style.top  = positionY + pt.y + "px";
      }
    });
  }

  function spc2cjs(v) {
    var p = v['players']
    var is_amiibo = is_amiibo_run(v);
    return {
      x: date_from_string(v['submitted']),
      y: DateTime.fromMillis(v['times']['primary_t'] * 1000).toUTC(),
      t: v['times']['primary_t'],
      id: p[0]['id'],
      run_id: v.id,
      amiibo: is_amiibo,
      //master: is_master_mode(v),
      url: v['weblink']
    };
  }

  function sort_by_x(a, b) {
    return a.x-b.x;
  }

  function zeroFill( number, width ) {
    width -= number.toString().length;
    if ( width > 0 ) {
      return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
    }
    return number + ""; // always return a string
  }

  function s2hms(v) {
    var s = Math.floor(v);
    let frac = Math.floor((v-s) * 1000);
    var m = Math.floor((s/60));
    s = s - m * 60;
    let h = Math.floor((m/60));
    m = m - h * 60;
    //console.log(v,h,m,s,frac);
    let out = "";
    if(h > 0) {
      out = `${h}:${zeroFill(m,2)}:${zeroFill(s,2)}.${zeroFill(frac,3)}`;
    } else {
      out = `${zeroFill(m,2)}:${zeroFill(s,2)}.${zeroFill(frac,3)}`;
    }
    return out;
  }

  function is_active(name) {
    if(xids.length > 0) {
      let id = player_name_to_id(name);
      let index = xids.findIndex(e => e.id === id);
      if(index != -1) {
        return xids[index].active;
      }
      return false;
    }
  }

  function new_label(xname, is_amiibo) {
    let ext = (is_amiibo) ? "" : " (no amiibo)";
    return `${xname}${ext}`;
  }

  function remove_active(xname) {
    //console.log("REMOVE",xname);
    for(var i = 0; i < 2; i++) {
      let label = new_label(xname, i == 0);
      let index = data.datasets.findIndex(e => e.label === label);
      if(index != -1) {
        data.datasets.splice(index, 1);
        let id = player_name_to_id(xname);
        let kndex = xids.findIndex(e => e.id === id);
        xids[kndex].active = false;
      }
    }
    chart_update();
  }

  function toggle_active(xname) {
    //console.log("TOGGLE",xname);
    if(is_active(xname)) {
      remove_active(xname);
    } else {
      add_active(xname);
    }
  }

  function add_active(name) {
    if(name !== undefined && name.length > 0) {
      let id = player_name_to_id(name);
      //console.log(name, id);
      let index = xids.findIndex(e => e.id === id);
      if(index != -1) {
        if(! xids[index].active) {
          xids[index].active = true;
          add_active_chart(name);
        }
      } else {
        console.log(`Error finding index for "${name}"`);
      }
    }
  }

  function chart_update() {
    if(chart !== undefined) {
      chart.update( );
    }
  }

  let _mode_      = 'j84q62n9';
  let mode        = undefined;
  //let _dlc_       = 'yn2vwvd8';
  //let no_dlc      = '4qyxve2l';
  //let yes_dlc     = 'mlny46j1';
  //let dlc         = undefined;
  let _amiibo_    = 'gnxrr7gn';
  let yes_amiibo  = '21dyvv31';
  let no_amiibo   = 'klr0jj0l';
  let amiibo      = undefined;


  
  function is_master_mode(run) {
    return run.values[_mode_] == master_mode;
  }
  function is_normal_mode(run) {
    return run.values[_mode_] == normal_mode;
  }
  function is_amiibo_run(run) {
    return run.values[_amiibo_] == yes_amiibo;
  }
  function is_no_amiibo_run(run) {
    return run.values[_amiibo_] == no_amiibo;
  }

  let _args_ = {};

  async function update_mode() {
    //console.log("UPDATE MODE");
    if(game_mode == normal_mode) {
      let x = await var_get("Mode", "Normal Mode");
      _args_ = Object.assign({}, _args_, x);
    } else if (game_mode == master_mode) {
      let x = await var_get("Mode", "Master Mode");
      _args_ = Object.assign({}, _args_, x);
    } else {
      //console.log("REMOVE GAME MODE");
      let x = await Object.keys( var_get("Mode", "Master Mode") )[0];
      delete _args_[x];
    }
  }

  function var_key(base, cat) {
    if(cat == "100") { return `${base} (100%)`; }
    if(cat == "amq") { return `${base} (AMQ)`; }
    if(cat == "as") { return `${base} (AS)`; }
    if(cat == "ad") { return `${base} (AD)`; }
    if(cat == "any") { return "DLC"; }
  }
  
  async function update_strict() {
    var key = var_key("Restrictions", category);
    let is_on = "Restricted";
    let is_off = "No Restrictions";
    if(category == "ad") {
      return;
    }
    if(strict_mode == strict_on) {
      let x = await var_get(key, is_on);
      _args_ = Object.assign({}, _args_, x);
    } else if(strict_mode == strict_off) {
      let x = await var_get(key, is_off);
      _args_ = Object.assign({}, _args_, x);
    } else {
      //let x = await Object.keys(var_get(key, is_off))[0];
      //delete _args_[x];
    }

  }
  
  async function update_dlc() {
    var key = var_key("DLC Goals", category);
    var original = "Original";
    var extended = "Extended";
    if(category == "any") {
      original = "No DLC";
      extended = "DLC";
    }
    if(dlc_mode == original_mode) {
      let x = await var_get(key, original);
      _args_ = Object.assign({}, _args_, x);
    } else if(dlc_mode == extended_mode) {
      let x = await var_get(key, extended);
      _args_ = Object.assign({}, _args_, x);
    } else {
      let x = await Object.keys(var_get(key, extended))[0];
      delete _args_[x];
    }
  }


  async function update_amiibo() {
    if(amiibo_on !== amiibo_off) {
      let x = await var_get("amiibo", (amiibo_on) ? "amiibo" : "No amiibo");
      _args_ = Object.assign({}, _args_, x);
    } else {
      let x = await Object.keys(await var_get("amiibo", "amiibo"))[0];
      if(amiibo_on) {
        delete _args_[x];
      } else {
        _args_[x] = '';
      }
    }
  }

  async function chart_update_option( option ) {
    if(option == 'mode') {
      await update_mode();
    } else if(option == 'amiibo') {
      await update_amiibo();
    } else if(option == 'dlc') {
      await update_dlc();
    } else if(option == 'strict') {
      await update_strict();
    }
    //console.log(_args_);
    charty_update();
  }

  $: {
    if(game_mode !== undefined) {
      chart_update_option('mode');
    }
  }
  $: {
    if(strict_mode !== undefined) {
      chart_update_option('strict');
    }
  }
  $: {
    if(dlc_mode !== undefined) {
      chart_update_option('dlc');
    }
  }
  $: {
    if(amiibo_on !== undefined || amiibo_off !== undefined ) {
      chart_update_option('amiibo');
    }
  }

  function by_player_id(run, id) {
    return run.players.some(p => p.id === id);
  }

  function dataset_new( label, pts, color, point_size, show_line, order, point_style ) {
    return {
      lineTension: 0.0,
      showLine: show_line,
      borderWidth: 1.0,
      borderColor: color,
      label: label,
      pointRadius: point_size,
      pointBackgroundColor: color,
      pointHitRadius: 20.0,
      hoverBorderWidth: 3,
      fill: false,
      data: pts,
      order: order,
      pointStyle: point_style,
    };
  }

  function add_active_chart_by_id( pid, xname = undefined ) {
    var color = xcolor(pid);
    if(xname === undefined) {
      xname = name( pid );
    }
    var styles = ['star', 'rect'];
    var styles = ['triangle', 'rect'];
    var ah_me_bo = [true,false];

    //console.log("ADD ACTIVE CHART BY ID", pid);
    for(var i = 0; i < styles.length; i++) {
      let ami = ah_me_bo[i];
      let style = styles[i];
      let label = new_label(xname, ami);
      let index = data.datasets.findIndex(e => e.label === label);
      if(index == -1) {
        var tmp = runs_get(_args_)
            .filter(run => by_player_id(run, pid))
            .filter(run => is_amiibo_run(run) == ami)
            .map(v => spc2cjs(v));
        if(tmp.length > 0) {
          tmp.sort(sort_by_x);
          data.datasets.push( dataset_new( label, tmp, color, 4.0, true, 1, style) );
        }
      }
    }
  }
  function add_active_chart(xname) {
    [xname].forEach((name,i) => {
      var pid = player_name_to_id(name);
      add_active_chart_by_id( pid );
      chart_update();
    });
  }

  function get_world_record( xruns ) {
    // Determine the World Record with Time
    xruns.sort( function(a,b) { return a.x - b.x } )
    let out = []
    if(xruns.length == 0) {
      return out;
    }
    let min_t = xruns[0].y;
    for(let i = 0; i < xruns.length; i++) {
      if(xruns[i].y <= min_t) {
        min_t = xruns[i].y;
        out.push(xruns[i]);
      }
    }
    return out;
  }

  $: {
    if(game_mode !== undefined) {
      data.datasets.length = 0;
      push_data = true;
    }
  }
  function charty_update() {

    let runs = runs_get();
    if(runs.length > 0 ) {
      var tmp = runs_get( _args_ ).map(run => spc2cjs(run));
      data.datasets.length = 0;
      push_data = true;
      for(var i = 0; i < 2; i++) {
        let ami = (i == 0) ? true : false;
        let symbol = (i == 0) ? "triangle" : "rect";
        var xtmp = tmp.filter(run => run.amiibo === ami);
        let label = "all_runs";
        if(!ami) {
          label += " (no amiibo)";
        }
        if(push_data) {
          let d1 = dataset_new(label, xtmp, "rgb(128,128,128)", 3.0, false, 3, symbol);
          data.datasets.push( d1 );
        } else {
          data.datasets[i].data = xtmp;
        }
      }
      let out = get_world_record( tmp );
      //console.log(tmp.length);
      let color = 'rgba(218,165,32,0.4)'; // Golden rod with alpha
      if(push_data) {
        let d2 = dataset_new("WR", out, color, 3.0, true, 2, 'circle');
        data.datasets.push( d2 );
      } else {
        data.datasets[2].data = out;
      }
      update_active_players();
      chart_update();
      push_data = false;

      xids_init();
    }
  }

  function update_active_players( ) {
    let active_players = xids.filter(p => p.active);
    if(active_players.length == 0) {
      return;
    }
    active_players.forEach(p => {
      let avar = [amiibo_on, amiibo_off];
      for(var i = 0; i < 2; i++) {
        let label = new_label(name(p.id), i == 0);
        let index = data.datasets.findIndex(e => e.label === label);
        if(index >= 0) {
          // Toggle Visibility
          let visible = chart.isDatasetVisible(index);
          //console.log(p.id, name(p.id), index, visible);
          chart.setDatasetVisibility(index, avar[i]);
        } else {
          add_active_chart_by_id( p.id );
        }
      }
    });
  }
  function min_time(pid) {
    let tmp = runs_get(_args_)
        .filter(run => by_player_id(run,pid))
        .map(v => v['times']['primary_t']);
    if(tmp.length > 0) {
      return Math.min.apply(Math, tmp);
    }
    return undefined;
  }

  function min_time_list() {
    let tmp = runs_get(_args_)
        .map(v => {return {t: v['times']['primary_t'], id: v['id']}});
    tmp.sort( function(a,b) { return a.t-b.t; } );
    return tmp.map(v => v.id );
  }

  function xids_init() {
    let pkeys = player_keys();
    let runs = runs_get(_args_);
    if(pkeys && runs.length > 0) {
      let tmp = pkeys.map(id => { return { t: min_time(id), id: id, active: false} } )
          .filter(v => v.t !== undefined);
      tmp.sort( function(a,b) { return a.t-b.t; } );
      xids = tmp;
    } else {
      xids = [];
    }
  }

  function create_popup_element(ch) {
    let parent = document.querySelector('#chart_parent');
    let tooltipEl = document.createElement('div');
    tooltipEl.style.background = 'rgba(0, 0, 0, 0.8)';
    tooltipEl.style.borderRadius = '3px';
    tooltipEl.style.color = 'white';
    tooltipEl.style.opacity = 1;
    tooltipEl.style.pointerEvents = 'none';
    tooltipEl.style.position = 'absolute';
    tooltipEl.style.display = "block";
    tooltipEl.style.zIndex = "0";
    const table = document.createElement('table');
    table.style.margin = '0px';
    tooltipEl.appendChild(table);
    if(ch) {
      parent.appendChild(tooltipEl);
    }
    return tooltipEl;
  }

  function tooltip_get_or_create(ch) {
    //let tooltipEl = ch.canvas.parentNode.parentNode.querySelector('#tooltip');
    let tooltipEl = document.querySelector('#tooltip');
    if (!tooltipEl) {
      tooltipEl = create_popup_element(ch);
      tooltipEl.setAttribute("id", "tooltip");
    }
    return tooltipEl;
  }

  function create_popup( tooltip, div ) {
    if (tooltip.body) {
      const bodyLines = tooltip.body.map(b => b.lines).slice(0,1); // Take only the first one

      const tableBody = document.createElement('tbody');
      bodyLines.forEach((body, i) => {
        const tr = document.createElement('tr');
        tr.style.backgroundColor = 'inherit';
        tr.style.borderWidth = 0;
        const td = document.createElement('td');
        td.style.borderWidth = 0;
        body.forEach(b => td.innerHTML += body );
        tr.appendChild(td);
        tableBody.appendChild(tr);
      });
      const tableRoot = div.querySelector('table');
      // Remove old children
      while (tableRoot.firstChild) {
        tableRoot.firstChild.remove();
      }
      // Add new children
      tableRoot.appendChild(tableBody);
    }
    if(tooltip.html) {
      const tableRoot = div.querySelector('table');
      // Remove old children
      while (tableRoot.firstChild) {
        tableRoot.firstChild.remove();
      }
      tableRoot.appendChild(tooltip.html);

    }
    const {offsetLeft: positionX, offsetTop: positionY} = chart.canvas;
    // Display, position, and set styles for font
    div.style.opacity = 1;
    div.style.display = "block";
    //let w = div.clientWidth;
    //let h = div.clientHeight;
    //console.log('POS',positionX, positionY, tooltip.caretX, tooltip.caretY);
    div.style.left = positionX + tooltip.caretX + 'px';
    div.style.top = positionY + tooltip.caretY + 'px';
    div.style.font = '9pt Helvetica, sans-serif';
    div.style.padding = tooltip.options.padding + 'px ' + tooltip.options.padding + 'px';

  }

  function external_tooltip(context) {
    // Tooltip Element
    let t = now();
    if( Math.abs(t - last_touch_start) < 500) {
      return;
    }
    const {chart, tooltip} = context;
    const tooltipEl = tooltip_get_or_create(chart);
    // Hide if no tooltip
    if (tooltip.opacity === 0) {
      tooltipEl.style.opacity = 0;
      tooltipEl.style.display = "none";
      return;
    }
    // Set Text
    create_popup( tooltip, tooltipEl );
  }

  var search_value = "";
  var search_value_lower = "";
  $: {
    search_value_lower = search_value.toLowerCase();
    xids = [...xids];
  }

  function fits_search( n ) {
    if(search_value.length == 0) {
      return true;
    }
    var nn = n.toLowerCase();
    return nn.includes( search_value_lower );
  }
  function xyz( id ) {
    return min_time( id ) && fits_search( name( id ) );
  }
  function count_runs( id ) {
    let tmp = runs_get(_args_).filter(run => run.players[0].id === id);
    return tmp.length;
  }
</script>

<style>
  .all {
    position: relative;
    height: 100%;
  }
  :global(a.redlink:link) {
    color: red;
  }
  :global(a.redlink:visited) {
    color: red;
  }
  .wrap {
    position: relative;
    margin: auto;
    width: 100%;
    height: 90vh;
  }
  @media screen and (min-width: 600px) {
    .all {
      position: relative;
      width: 100%;
      height: 100%;
    }
    .wrap {
      position: relative;
      height: 70vw;
      margin: auto;
      width: 90vw;
    }
  }
  #popup {
    display: none;
    justify-content: center;
    flex-direction: column;
    align: center;
    padding: 4px;
    border: 0px solid red;
    border-radius: 5px;
    background: rgba(0,0,0,0.7);
    color: white;
    font-size: 0.8em;
    font-family: Arial, sans-serif;
    position: absolute;
    max-width: 250px;
    max-height: 250px;
  }
  #twrap {
    overflow-y: scroll;
    max-height: 40vh;
    margin: auto;

  }
  #table {
    overflow-y: scroll;
    position: relative;
    display: table;
    width: 100%;
  }
  @media screen and (min-width: 600px) {
    #twrap {
      overflow-y: scroll;
      max-height: 20vh;
      width: 60%;
      margin: auto;
    }
    #table {
      overflow-y: scroll;
      position: relative;
      display: table;
      width: 100%;
    }
  }
  .row {
    display: table-row;
    width: 50%;
  }
  .col {
    display: table-cell;
    border-bottom: 1px solid black;
  }
  .header {
    font-size: 0.9em;
    text-align: center;
    margin-bottom: 15px;
  }
  @media screen and (min-width: 600px) {
    .header {
      margin-left: auto;
      margin-right: auto;
      width: 70%;
    }
  }
  .options {
    display: flex;
  }
  .option {
    display: flex;
    flex-direction: column;
    margin-left: 20px;
  }
  .option_fill {
    flex-grow: 1;
  }
  button {
    font-size: 0.8em;
  }
  .slide_right {
    position: absolute;
    right: 0px;
    top: 0px;
    margin: 25px;
  }
</style>
<div class="header">
  <h2>BotW {title} Runs</h2>
  <p>
  Tap/Click on a run (point) to get to the video or highlight all of a runner's submissions.
  All data is derived from <a href="https://speedrun.com">speedrun.com</a> through the <a href="https://github.com/speedruncomorg/api">API</a>.
  Data last updated on June 24, 2021.
  </p>
</div>
<div class="slide_right">
  <div><a href="?cat=any">Any%</a></div>
  <div><a href="?cat=ad">AD</a></div>
  <div><a href="?cat=amq">AMQ</a></div>
  <div><a href="?cat=as">AS</a></div>
  <div><a href="?cat=100">100%</a></div>
</div>

<div class="wrap" id="chart_parent">
  <div class="all">
    <canvas id="chart"></canvas>
  </div>
</div>
<div style="margin: auto; width: 95vw;" class="options">
  <div class="option_fill">
    <button on:click={() => chart.resetZoom()} >Reset Zoom</button>
  </div>
  <div class="option">
    <input type="text" name="search" bind:value="{search_value}" placeholder="Search runners..." id="search" />
  </div>
  {#if category == "any" }
    <div class="option">
      <div><input type="checkbox" name="amiibo_on" bind:checked={amiibo_on}/> Amiibo</div>
      <div><input type="checkbox" name="amiibo_off" bind:checked={amiibo_off}/> No Amiibo</div>
    </div>
  {/if}
  {#if category == "any" }
    <div class="option">
      <div><input type="radio" bind:group={game_mode} value={normal_mode}/> Normal Mode</div>
      <div><input type="radio" bind:group={game_mode} value={master_mode}/> Master Mode</div>
    </div>
  {/if}
  {#if category == "100" || category == "amq" || category == "as" || category == "ad" }
    <div class="option">
      <div><input type="radio" bind:group={dlc_mode} value={original_mode}/> Original</div>
      <div><input type="radio" bind:group={dlc_mode} value={extended_mode}/> Extended</div>
    </div>
  {/if}
  {#if category == "amq" || category == "as"}
    <div class="option">
      <div><input type="radio" bind:group={strict_mode} value={strict_off}/> No Restrictions</div>
      <div><input type="radio" bind:group={strict_mode} value={strict_on}/> Restricted</div>
    </div>
  {/if}
  <div class="option option_fill"></div>
</div>
<div id="twrap">
  <div id="table">
    {#each xids as p (p.id) }
      {#if xyz(p.id)}
        <div class="row">
          <div class="col">
            <input type="checkbox"
                   id={name(p.id)}, name={name(p.id)}
                   checked={ is_active(name(p.id)) ? "checked" : "" }
                   on:change={() => { toggle_active(name(p.id)) } }>
          </div>
          <div class="col">
            <a href="{player_get(p.id).data.weblink}" target="_blank">{name(p.id)}</a>
          </div>
          <div class="col">{s2hms(min_time(p.id))}</div>
          <div class="col">{count_runs(p.id)}</div>
        </div>
      {/if}
    {/each}
  </div>
</div>
<div style="margin-top: 60px"></div>

<div id="tmp"></div>
