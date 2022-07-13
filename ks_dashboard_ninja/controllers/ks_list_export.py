
import re
import datetime
import io
import json
import operator

from odoo.addons.web.controllers.main import ExportFormat,serialize_exception, ExportXlsxWriter
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from odoo.tools import pycompat


class KsListExport(ExportFormat, http.Controller):

    def base(self, data, token):
        params = json.loads(data)
        header,list_data = operator.itemgetter('header','chart_data')(params)
        list_data = json.loads(list_data)
        # chart_data['labels'].insert(0,'Measure')
        columns_headers = list_data['label']
        import_data = []

        for dataset in list_data['data_rows']:
            # dataset['data'].insert(0, dataset['label'])
            import_data.append(dataset['data'])

        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(header))),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})


class KsListExcelExport(KsListExport, http.Controller):

    # Excel needs raw data to correctly handle numbers and date values
    raw_data = True

    @http.route('/ks_dashboard_ninja/export/list_xls', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'application/vnd.ms-excel'

    def filename(self, base):
        return base + '.xls'

    def from_data(self, fields, rows):
        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value


class KsListCsvExport(KsListExport, http.Controller):

    @http.route('/ks_dashboard_ninja/export/list_csv', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.csv'

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str)    and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()
