import pyblish.api


class AutoFixAction(pyblish.api.Action):
    """Run a plugin's fix on every failed instance."""
    label = "Auto-fix"
    def process(self, context, plugin):
        self.log.info("Running {} auto-fix".format(plugin))
        if getattr(plugin, 'auto_fix'):
            instances = [ i for i in context.data["results"] if i["plugin"] == plugin]
            failed_instances = [i for i in instances if not i["success"]]
            for i in failed_instances:
                plugin.auto_fix(i.get('instance'), self)
