/* Plotly axis style */
const axisTemplate = {
    autorange: true,
    showgrid: true,
    zeroline: false,
    gridwidth: 2,
    linecolor: 'black',
    showticklabels: true,
    ticks: '',
    title: 'latitude'
};

/* json data for the play and pause buttons */


const updatemenus = [{
    "x": 0.1,
    "y": 0,
    "yanchor": "top",
    "xanchor": "center",
    "showactive": false,
    "direction": "right",
    "type": "buttons",
    "pad": {"t": 100, "r": 10},
    "buttons": [{
      "method": "animate",
      "args": [null, {
        "fromcurrent": true,
        "transition": {
          "duration": 400,
          "easing": "quadratic-in-out"
        },
        "frame": {
          "duration": 100,
          "redraw": true,
        }
      }],
      "label": "Play"
    }, {
      "method": "animate",
      "args": [
        [null],
        {
          "mode": "immediate",
          "transition": {
            "duration": 0
          },
          "frame": {
            "duration": 0,
            "redraw": false
          }
        }
      ],
      "label": "Pause"
    }]
}]
    
/* Layout of trace */
const layout = {
    title: 'Salinity',
    margin: {
      t: 100,
      r: 100,
      b: 100,
      l: 100
    },   
    yaxis: axisTemplate,
    xaxis: Object.assign({}, axisTemplate, {title:'longitude'}),

    showlegend: false,
    width: 600,
    height: 600,
    autosize: false,
    

  
    
};