from flask import render_template
from flask_login import login_required
import pandas as pd
import config
from utils import get_file_last_updated
from utils.format_utils import Formatter
from routes import flavor_bp

@flavor_bp.route('/list-all-flavors', methods=['GET'])
@login_required
def list_all_flavors():
    """
    List all flavors
    
    Returns:
        Response: Rendered template with flavors
    """
    flavor_last_updated = get_file_last_updated(config.FLAVORS_FILE_PATH)
    
    flavor_data = pd.read_csv(config.FLAVORS_FILE_PATH, delimiter=config.CSV_DELIMITER)
    
    formatter = Formatter()
    flavor_data['RAM'] = flavor_data['RAM'].apply(formatter.format_ram)
    flavor_data['Is Public'] = flavor_data['Is Public'].apply(formatter.format_public)
    flavor_data['Swap'] = flavor_data['Swap'].apply(formatter.format_swap)
    flavor_data['Properties'] = flavor_data['Properties'].apply(formatter.format_properties)
    
    flavor_data = flavor_data.to_dict(orient='records')
    return render_template('list_all_flavors.html', 
                          flavor_data=flavor_data, 
                          flavor_last_updated=flavor_last_updated)
