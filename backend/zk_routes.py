from flask import Blueprint, request, jsonify
from celery.result import AsyncResult
from celery_app import celery
from zk_tasks import (
    generate_rust_zk_proof_async,
    verify_rust_zk_proof_async,
    issue_eidas_tsa_token_async
)

zk_bp = Blueprint('zk_bp', __name__)

@zk_bp.route('/api/v1/zk/prove', methods=['POST'])
def api_generate_proof():
    data = request.get_json() or {}
    attribute = data.get('attribute', 'default_citizen_identity')
    threshold = int(data.get('threshold', 18))
    
    # Spuštění úlohy asynchronně přes Celery/Redis
    task = generate_rust_zk_proof_async.delay(attribute, threshold)
    return jsonify({
        "task_id": task.id,
        "status": "queued",
        "message": "ZK proof generation dispatched to Celery worker."
    }), 202

@zk_bp.route('/api/v1/zk/verify', methods=['POST'])
def api_verify_proof():
    data = request.get_json() or {}
    attribute = data.get('attribute', '')
    threshold = int(data.get('threshold', 18))
    commitment = data.get('commitment', '')
    
    task = verify_rust_zk_proof_async.delay(attribute, threshold, commitment)
    return jsonify({
        "task_id": task.id,
        "status": "queued",
        "message": "ZK verification dispatched to Celery worker."
    }), 202

@zk_bp.route('/api/v1/zk/tsa', methods=['POST'])
def api_issue_tsa():
    data = request.get_json() or {}
    commitment = data.get('commitment', '')
    
    task = issue_eidas_tsa_token_async.delay(commitment)
    return jsonify({
        "task_id": task.id,
        "status": "queued",
        "message": "eIDAS TSA token issuance dispatched to Celery worker."
    }), 202

@zk_bp.route('/api/v1/zk/task/<task_id>', methods=['GET'])
def api_get_task_status(task_id):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.ready():
        return jsonify({
            "task_id": task_id,
            "status": "completed",
            "result": task_result.result
        }), 200
    else:
        return jsonify({
            "task_id": task_id,
            "status": task_result.status,
            "message": "Task is still processing in background."
        }), 202
