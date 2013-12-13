/**
 * Main application file for: minnpost-hazmat
 *
 * This pulls in all the parts
 * and creates the main object for the application.
 */
define('minnpost-hazmat', ['underscore', 'Ractive', 'helpers',
  'text!templates/application.mustache',
  'text!templates/loading.mustache'],
  function(_, Ractive, helpers,
    tApplication, tLoading) {

  // Constructor for app
  var App = function(options) {
    this.options = options;
    this.el = this.options.el;
    if (this.el) {
      this.$el = $(this.el);
    }
  };

  // Extend with helpers
  _.extend(App.prototype, helpers);

  // Start function
  App.prototype.start = function() {
    // Create application view
    this.view = new Ractive({
      el: this.$el,
      template: tApplication,
      data: {

      },
      partials: {
        loading: tLoading
      }
    });

  };

  return App;
});
