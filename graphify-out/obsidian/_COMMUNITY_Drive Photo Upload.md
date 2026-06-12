---
type: community
cohesion: 0.22
members: 10
---

# Drive Photo Upload

**Cohesion:** 0.22 - loosely connected
**Members:** 10 nodes

## Members
- [[AnalyzeMealResponse_1]] - code - api/routers/meals.py
- [[Google Drive upload service for meal photos.  Uploads a JPEGPNG image to the]] - rationale - api/services/drive_service.py
- [[Return a cached Google Drive API v3 service client.]] - rationale - api/services/drive_service.py
- [[Upload a meal photo to Google Drive and return its public URL.      Creates a]] - rationale - api/services/drive_service.py
- [[Upload a meal photo, store it in Google Drive, and run AI vision analysis.]] - rationale - api/routers/meals.py
- [[UploadFile]] - code - api/routers/meals.py
- [[_get_drive_service()]] - code - api/services/drive_service.py
- [[analyze_meal_endpoint()]] - code - api/routers/meals.py
- [[drive_service.py]] - code - api/services/drive_service.py
- [[upload_meal_image()]] - code - api/services/drive_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Drive_Photo_Upload
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Meal Integration Tests]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]

## Top bridge nodes
- [[upload_meal_image()]] - degree 7, connects to 2 communities
- [[analyze_meal_endpoint()]] - degree 6, connects to 2 communities
- [[drive_service.py]] - degree 6, connects to 2 communities