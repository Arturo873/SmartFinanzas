class ERPRouter:
    """
    Un router que controla las operaciones de base de datos en los modelos de las 
    aplicaciones del ERP (catalogo, inventario, proveedores).
    """
    route_app_labels = {'catalogo', 'inventario', 'proveedores'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'erp_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'erp_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'erp_db'
        
        # El resto de apps de django y de AppWeb iran a default
        if db == 'erp_db':
            return False
            
        return None
