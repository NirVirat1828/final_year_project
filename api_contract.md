# API Contract

## `/api/v1/analyze-batch`

### POST /api/v1/analyze-batch
- Summary: Analyze Batch
- Request body:
- Content type: application/json
- Schema: InferenceRequest
- Responses:
  - `200`
    - Schema: InferenceResponse
  - `422`
    - Schema: HTTPValidationError

## `/api/v1/health`

### GET /api/v1/health
- Summary: Health Check
- Request body:
No request body.
- Responses:
  - `200`
    - Schema: object
