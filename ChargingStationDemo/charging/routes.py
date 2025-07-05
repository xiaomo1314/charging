from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from . import charging_bp
from extensions import db
from models import Station, UseInfo


@charging_bp.route('/stations')
@login_required
def stations():
    # 页面不传 stations，前端选择区域和类型后请求充电桩数据
    return render_template('charging/stations.html')


@charging_bp.route('/api/stations')
@login_required
def api_stations():
    area = request.args.get('area')
    facility_type = request.args.get('type')  # 新增类型过滤参数，字符串 '0' 或 '1'

    if not area:
        return jsonify({'error': '缺少区域参数'}), 400

    query = Station.query.filter_by(location=area)
    if facility_type in ['0', '1']:
        query = query.filter_by(facilitytype=int(facility_type))

    stations = query.all()
    stations_data = [
        {
            'stationid': s.stationid,
            'facilitytype': s.facilitytype,
            'location': s.location
            # 这里可以根据需要增加更多字段，比如状态等
        } for s in stations
    ]
    return jsonify(stations_data)


@charging_bp.route('/simulate/<station_id>', methods=['POST'])
@login_required
def simulate(station_id):
    try:
        data = request.get_json() or {}
        duration_minutes = data.get('duration')
        if not isinstance(duration_minutes, int) or not (30 <= duration_minutes <= 180):
            return jsonify({'error': '无效的充电时长'}), 400

        start = datetime.now()
        end = start + timedelta(minutes=duration_minutes)

        cost = round(duration_minutes / 60 * 20, 2)

        useinfo = UseInfo(
            uid=current_user.uid,
            stationid=station_id,
            begintime=start,
            endtime=end,
            money=cost
        )
        db.session.add(useinfo)
        db.session.commit()

        flash(f'充电成功！充电时长 {duration_minutes} 分钟，费用 {cost} 元。')
        return redirect(url_for('charging.history'))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器内部错误，请稍后重试'}), 500


@charging_bp.route('/history')
@login_required
def history():
    records = UseInfo.query.filter_by(uid=current_user.uid).order_by(UseInfo.begintime.desc()).all()
    return render_template('charging/history.html', records=records)
