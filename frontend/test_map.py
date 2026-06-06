import flet as ft
import flet.map as ft_map
from config import MAPTILER_API_KEY
print('import ok')
try:
    m = ft_map.Map(
        expand=True,
        initial_center=ft_map.MapLatitudeLongitude(-34.588, -59.704),
        initial_zoom=13,
        interaction_configuration=ft_map.MapInteractionConfiguration(flags=ft_map.MapInteractiveFlag.ALL),
        layers=[
            ft_map.TileLayer(
                url_template=f"https://api.maptiler.com/maps/hybrid/{'{'}z{'}'}/{ '{'}x{'}'}/{ '{'}y{'}'}.jpg?key={MAPTILER_API_KEY}",
                fallback_url='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                error_image_src='https://upload.wikimedia.org/wikipedia/commons/8/89/No_image_available.svg',
                additional_options={'userAgentPackageName': 'com.amin.campomovil'},
                on_image_error=lambda e: print('err', e.data),
            ),
        ],
    )
    print('Map created', type(m))
except Exception as e:
    import traceback; traceback.print_exc()
