# Facebook Graph API – Retrieve Page Post Data

This guide lists all available fields and steps to retrieve a single post object from a Facebook Page using the Graph API.

---

## Basic Post Fields

```
| **Field**       | **Type**        | **Description**                                                    |
| --------------- | --------------- | ------------------------------------------------------------------ |
| `id`            | token (Post ID) | The unique ID of the post.                                         |
| `from`          | User | Page     | The ID of the user, page, group, or event that published the post. |
| `created_time`  | datetime        | The time the post was published (UNIX timestamp).                  |
| `updated_time`  | datetime        | The time the post was last updated (e.g., after a comment).        |
| `permalink_url` | uri             | Permanent URL of the post.                                         |
| `message`       | string          | The message written in the post.                                   |
| `story`         | string          | Text of automatically generated stories (e.g., “became friends”).  |
| `story_tags`    | list            | Tags within the story text.                                        |
| `message_tags`  | list            | Profiles tagged in the message.                                    |
| `privacy`       | Privacy         | Privacy settings for the post.                                     |

```

🔗 [Check Official Docs for All Available Fields](https://developers.facebook.com/docs/graph-api/reference/page-post/)

---

## Setup & Access Tokens

## Credentials (use these long-lived tokens for requests and proceed to step 2)

```
LONGLIVED_PAGE_ACCESS_TOKEN=EAAQfIUidhhwBPoZC06PPSDZCNag336x1Yogl774VZAZAo8alQxX0PBjryBKhc7ViLRVVI6AIIpoKWeWvi27Htl7ZC16seoSHuDZAsFiCci0BRicQ59WGx9uRRqa0mqItQZADolnIBfMiQp7iEgrYtB01Mui7MpGcuHff3CpWwIwpc4drRbN4T6tUhuotZCE6EzKdZCTeY36Dc

LONGLIVED_USER_ACCESS_TOKEN=EAAQfIUidhhwBPkjz3I1XaFc9zi7oaEX9azBlKY0qQk4AnsbLZCaj57QjFdU7yKTC9fSZC0aMBRZCK7q5dykl7ng96AZA3DdUiy2KCJMQjlRpkJFZA0ZAl2yYPU2s7D03L76VZAblRkfO39EsZA6PbfnZCD7dD4gL8ZCrda3961D5ZByT8kFBNsV0Ado2vbtcK9ilKN3
```

## Sample Request - (You can use POSTMAN or Graph API Explorer Tool)

### Step 1. Get a User Access Token

Generate a **User Access Token** using the [Graph API Explorer Tool](https://developers.facebook.com/tools/explorer).

USER_ACCESS_TOKEN=

### Step 2. Get a Page Access Token and Page ID

Use the **User Access Token** from Step 1.

```sql
GET "https://graph.facebook.com/v24.0/me/accounts?access_token={USER_ACCESS_TOKEN}"
```

**Example Response:**

```json
{
  "data": [
    {
      "access_token": "EAAQfIUidhhwBPiZBk....",
      "category": "Software",
      "category_list": [{ "id": "2211", "name": "Software" }],
      "name": "Test Page",
      "id": "7389290....",
      "tasks": [
        "ADVERTISE",
        "ANALYZE",
        "CREATE_CONTENT",
        "MESSAGING",
        "MODERATE",
        "MANAGE"
      ]
    }
  ],
  "paging": {
    "cursors": {
      "before": "QVFIU0N4a1ZA...",
      "after": "QVFIU0N4a1ZAkW..."
    }
  }
}
```

## Step 3. Get Page Feed and Select a Post ID

Use the Page ID and Page Access Token from Step 2.

```sql
GET "https://graph.facebook.com/v24.0/{PAGE_ID}/feed?access_token={PAGE_ACCESS_TOKEN}"
```

Example Response:

```json
{
  "data": [
    {
      "created_time": "2025-09-19T21:53:31+0000",
      "message": "kdot",
      "id": "738929032644857_12210280533....."
    },
    {
      "created_time": "2025-09-18T19:17:18+0000",
      "message": "sea",
      "id": "738929032644857_12210238263....."
    }
  ],
  "paging": {
    "cursors": {
      "before": "QVFIU0ROR1k0TnJ.....",
      "after": "QVFIU05PeXh5aENiN1ZAKb..."
    }
  }
}
```

## Step 4. Get Post Data

Use the Post ID and Page Access Token to get detailed post data.

```sql
GET "https://graph.facebook.com/v24.0/{POST_ID}?fields=id,message,created_time,permalink_url,attachments,likes.summary(true),comments.summary(true),shares&access_token={PAGE_ACCESS_TOKEN}"
```

Example Response:

```json
{
  "id": "738929032644857_122102805332....",
  "message": "kdot",
  "created_time": "2025-09-19T21:53:31+0000",
  "permalink_url": "https://www.facebook.com/122107977446989821/posts/122102805.....",
  "attachments": {
    "data": [
      {
        "media": {
          "image": {
            "height": 552,
            "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/55.846_1221028....._6636302388....._n.jpg",
            "width": 717
          }
        },
        "subattachments": {
          "data": [
            {
              "media": {
                "image": {
                  "height": 552,
                  "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/550012846_122102805...._66363023882......_n.jpg",
                  "width": 717
                }
              },
              "target": {
                "id": "1221028050.....",
                "url": "https://www.facebook.com/photo.php?fbid=122102805020.....&set=a.1221017190089....&type=3"
              },
              "type": "photo",
              "url": "https://www.facebook.com/photo.php?fbid=122102805.....&set=a.122101719008.....&type=3"
            },
            {
              "media": {
                "image": {
                  "height": 694,
                  "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/549523301_1221028052.....1_3005173....._n.jpg",
                  "width": 507
                }
              },
              "target": {
                "id": "1221028052.....",
                "url": "https://www.facebook.com/photo.php?fbid=12210280520....&set=a.1221017190089....&type=3"
              },
              "type": "photo",
              "url": "https://www.facebook.com/photo.php?fbid=1221028052....&set=a.1221017....&type=3"
            }
          ]
        },
        "target": {
          "id": "12210280533.....",
          "url": "https://www.facebook.com/122107977446989821/posts/1221028....."
        },
        "title": "Photos from Test Page's post",
        "type": "album",
        "url": "https://www.facebook.com/122107977446989821/posts/12210280533...."
      }
    ]
  },
  "likes": {
    "data": [],
    "summary": {
      "total_count": 0,
      "can_like": true,
      "has_liked": true
    }
  },
  "comments": {
    "data": [],
    "summary": {
      "order": "chronological",
      "total_count": 0,
      "can_comment": true
    }
  }
}
```
