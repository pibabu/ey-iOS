to-do


new index.html on container -> pushed to fastapi -> new frontend in browser


fast api Trigger:

1. Initial Standard Frontend
# FastAPI serves default HTML to everyone initially
@app.get("/")
async def get_frontend(request: Request):
    user_hash = request.cookies.get("user_hash")
    
    if not user_hash:
        # No user yet, serve default
        with open('default_index.html', 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    # User exists - check if they have custom HTML
    custom_html = await get_user_custom_html(user_hash)
    
    if custom_html:
        return HTMLResponse(content=custom_html)
    else:
        # Fall back to default
        with open('default_index.html', 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
2. Reading Custom HTML from Container
async def get_user_custom_html(user_hash: str) -> str | None:
    """Read custom index.html from user's container workspace."""
    
    # Get container ID
    result = subprocess.run([
        "docker", "ps", "-q",
        "--filter", f"label=user_hash={user_hash}"
    ], capture_output=True, text=True, timeout=5)
    
    container_id = result.stdout.strip()
    if not container_id:
        return None
    
    # Try to read custom HTML from workspace
    result = subprocess.run([
        "docker", "exec", container_id,
        "cat", "/workspace/index.html"
    ], capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout
    
    return None
3. User Triggers Custom HTML

User types in chat: "Use the HTML file at /workspace/custom/new_ui.html"
@router.post("/api/set-custom-frontend")
async def set_custom_frontend(
    request: Request,
    file_path: str
):
    user_hash = request.cookies.get("user_hash")
    
    # Get container
    container_id = get_container_id(user_hash)
    
    # Read the file from container
    result = subprocess.run([
        "docker", "exec", container_id,
        "cat", file_path
    ], capture_output=True, text=True, timeout=5)
    
    if result.returncode != 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    html_content = result.stdout
    
    # Store preference in container metadata or database
    # Option 1: Write to a known location
    subprocess.run([
        "docker", "exec", container_id,
        "cp", file_path, "/workspace/index.html"
    ], timeout=5)
    
    # Option 2: Store in database
    # db.set_user_preference(user_hash, "custom_html_path", file_path)
    
    return {"status": "success", "message": "Frontend updated"}