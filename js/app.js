/**
 * Main application file for: minnpost-hazmat
 *
 * This pulls in all the parts
 * and creates the main object for the application.
 */
define('minnpost-hazmat', [
  'underscore', 'jquery', 'Ractive', 'Highcharts', 'helpers',
  'text!../data/question-incidents_by_year.json',
  'text!../data/question-incidents_by_material.json',
  'text!templates/application.mustache',
  'text!templates/loading.mustache'
],
function(_, $, Ractive, Highcharts, helpers,
  dByYear, dByMaterial,
  tApplication, tLoading) {

  // Parse the incoming data
  var pData = {
    byYear: JSON.parse(dByYear),
    byMaterial: JSON.parse(dByMaterial)
  };

  // Constructor for app
  var App = function(options) {
    this.options = _.extend(this.defaultOptions, options);
    this.el = this.options.el;
    if (this.el) {
      this.$el = $(this.el);
    }
  };

  // Extend with helpers
  _.extend(App.prototype, helpers);

  // Start function
  _.extend(App.prototype, {
    start: function() {
      var thisApp = this;

      // Create application view
      this.view = new Ractive({
        el: this.$el,
        template: tApplication,
        data: {
          sources: pData,
          stats: this.makeStats()
        },
        partials: {
          loading: tLoading
        }
      });

      // Observe data to make some charts
      this.view.observe('sources.byYear', function(n, o) {
        var options;

        if (!_.isUndefined(n)) {
          options = _.clone(thisApp.options.highChartOptions);
          options = $.extend(true, options, {
            series: [{
              name: 'Incidents per year',
              data: n
            }]
          });
          thisApp.$el.find('.chart-incidents-by-year').highcharts(options);
        }
      });

      this.view.observe('sources.byMaterial', function(n, o) {
        var options;

        if (!_.isUndefined(n)) {
          options = _.clone(thisApp.options.highChartOptions);
          options = $.extend(true, options, {
            chart: {
              type: 'bar'
            },
            series: [{
              name: 'Incidents involving specific materials',
              data: _.first(n, 10)
            }]
          });
          thisApp.$el.find('.chart-incidents-by-material').highcharts(options);
        }
      });
    },

    // Make stats
    makeStats: function() {
      return {
        // There are two years that have the max
        //topYear: _.max(pData.byYear, function(d) { return d[1]; })[0],
        topYearCount: _.max(pData.byYear, function(d) { return d[1]; })[1]
      };
    },

    // Extend default options
    defaultOptions: {
      highChartOptions: {
        chart: {
          type: 'line',
          style: {
            fontFamily: '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
            color: '#BCBCBC'
          }
        },
        colors: ['#094C86', '#BCBCBC'],
        credits: {
          enabled: false
        },
        title: {
          enabled: false,
          text: ''
        },
        legend: {
          borderWidth: 0
        },
        plotOptions: {
          line: {
            lineWidth: 4,
            states: {
              hover: {
                lineWidth: 5
              }
            },
            marker: {
              fillColor: '#ffffff',
              lineWidth: 2,
              lineColor: null,
              symbol: 'circle',
              enabled: false,
              states: {
                hover: {
                  enabled: true
                }
              }
            }
          }
        },
        xAxis: {
          title: { },
          minPadding: 0,
          maxPadding: 0,
          type: 'category',
          labels: {
            formatter: function() {
              return this.value;
            }
          }
        },
        yAxis: {
          title: {
            enabled: false,
            text: '[Update me]',
            margin: 40,
            style: {
              color: 'inherit',
              fontWeight: 'normal'
            }
          },
          min: 0,
          gridLineColor: '#BCBCBC'
        },
        tooltip: {
          //shadow: false,
          //borderRadius: 0,
          //borderWidth: 0,
          style: {},
          useHTML: true,
          formatter: function() {
            return this.key + ': <strong>' + this.y + '</strong>';
          }
        }
      }
    }
  });

  return App;
});
