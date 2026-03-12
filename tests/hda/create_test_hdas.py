import hou
import os

def create_test_hdas():
    hda_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(hda_dir):
        os.makedirs(hda_dir)

    # Setup contexts
    obj = hou.node("/obj")
    
    # SOP context
    geo = obj.createNode("geo", "test_geo_context_v3")
    
    # DOP context
    dop = obj.createNode("dopnet", "test_dop_context_v3")
    
    # COP context
    if not hou.node("/img"):
        hou.node("/").createNode("img", "img")
    img_net = hou.node("/img").createNode("img", "test_img_context_v3")
    
    # LOP context
    if not hou.node("/stage"):
        hou.node("/").createNode("lopnet", "stage")
    stage = hou.node("/stage")

    # TOP context
    top_net = obj.createNode("topnet", "test_top_context_v3")

    hdas = [
        {"name": "test_sop_node", "parent": geo, "label": "Test SOP Node", "namespace": "test", "version": "1.0.0"},
        {"name": "test_obj_node", "parent": obj, "label": "Test OBJ Node", "namespace": "test", "version": "1.1.0"},
        {"name": "test_dop_node", "parent": dop, "label": "Test DOP Node", "namespace": "test", "version": "2.0.0"},
        {"name": "test_lop_node", "parent": stage, "label": "Test LOP Node", "namespace": "test", "version": "1.0.0"},
        {"name": "test_cop_node", "parent": img_net, "label": "Test COP Node", "namespace": "test", "version": "1.0.0"},
        {"name": "test_top_node", "parent": top_net, "label": "Test TOP Node", "namespace": "test", "version": "1.0.0"},
        {"name": "another_sop", "parent": geo, "label": "Another SOP", "namespace": "dev", "version": "0.1.0"},
        {"name": "simple_node", "parent": geo, "label": "Simple Node", "namespace": None, "version": None},
        {"name": "versioned_node", "parent": geo, "label": "Versioned Node v1", "namespace": "test", "version": "1.0.0"},
        {"name": "versioned_node", "parent": geo, "label": "Versioned Node v1.0.1", "namespace": "test", "version": "1.0.1"},
        {"name": "versioned_node", "parent": geo, "label": "Versioned Node v2", "namespace": "test", "version": "2.0.0"},
        {"name": "special-chars-node", "parent": geo, "label": "Special Chars Node", "namespace": "test", "version": "1.0.0"},
    ]

    for hda in hdas:
        parent = hda["parent"]
        unique_name = hda["name"]
        if hda["version"]:
            unique_name += "_" + hda["version"].replace(".", "_")
        
        # Use subnet for all as it's a generic container valid in most contexts
        node = parent.createNode("subnet", unique_name)
        
        # Build full name: [namespace::]name[::version]
        full_name = hda["name"]
        if hda["namespace"]:
            full_name = f"{hda['namespace']}::{full_name}"
        if hda["version"]:
            full_name = f"{full_name}::{hda['version']}"
            
        hda_filename_base = hda["name"]
        if hda["namespace"]:
            hda_filename_base = f"{hda['namespace']}_{hda_filename_base}"
        if hda["version"]:
            hda_filename_base = f"{hda_filename_base}_{hda['version'].replace('.', '_')}"
            
        hda_file = os.path.join(hda_dir, f"{hda_filename_base}.hda")
        
        if os.path.exists(hda_file):
            os.remove(hda_file)

        try:
            node.createDigitalAsset(
                name=full_name,
                hda_file_name=hda_file,
                description=hda["label"]
            )
            print(f"Created HDA: {full_name} at {hda_file}")
        except hou.OperationFailed as e:
            print(f"Failed to create {full_name}: {e}")

if __name__ == "__main__":
    create_test_hdas()
