from .models import SiteInformation


def site_info(request):
    """Make site information available to all templates"""
    site_info = SiteInformation.get_instance()
    return {
        "site_info": site_info,
        "tva_rate": site_info.tva_rate,
    }
