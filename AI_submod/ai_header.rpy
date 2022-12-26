# Register the updater
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MonikAI",
            user_name="Rubiksman78",
            repository_name="Monik.A.I",
            update_dir="",
        )