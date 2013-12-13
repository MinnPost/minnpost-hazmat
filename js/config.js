/**
 * RequireJS config which maps out where files are and shims
 * any non-compliant libraries.
 */
require.config({
  shim: {
    'underscore': {
      exports: '_'
    },
    'Highcharts': {
      exports: 'Highcharts',
      'deps': [ 'jquery']
    }
  },
  baseUrl: 'js',
  paths: {
    'requirejs': '../bower_components/requirejs/require',
    'text': '../bower_components/text/text',
    'jquery': '../bower_components/jquery/jquery.min',
    'underscore': '../bower_components/underscore/underscore-min',
    'Ractive': '../bower_components/ractive/build/Ractive-legacy.min',
    'Highcharts': '../bower_components/highcharts/highcharts',
    'minnpost-hazmat': 'app'
  }
});
