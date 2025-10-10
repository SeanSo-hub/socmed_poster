# Facebook Graph API
This document lists all available fields you can request when retrieving a single post object from a Facebook Page using the Graph API

## Basic info fields

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

[Check the documentation for all available fields](https://developers.facebook.com/docs/graph-api/reference/page-post/)

# -----------------------------------------------------------------------------

# Sample Request

## Credentials (use these long-lived tokens for requests and proceed to step 2)

LONGLIVED_PAGE_ACCESS_TOKEN=EAAQfIUidhhwBPoZC06PPSDZCNag336x1Yogl774VZAZAo8alQxX0PBjryBKhc7ViLRVVI6AIIpoKWeWvi27Htl7ZC16seoSHuDZAsFiCci0BRicQ59WGx9uRRqa0mqItQZADolnIBfMiQp7iEgrYtB01Mui7MpGcuHff3CpWwIwpc4drRbN4T6tUhuotZCE6EzKdZCTeY36Dc

LONGLIVED_USER_ACCESS_TOKEN=EAAQfIUidhhwBPkjz3I1XaFc9zi7oaEX9azBlKY0qQk4AnsbLZCaj57QjFdU7yKTC9fSZC0aMBRZCK7q5dykl7ng96AZA3DdUiy2KCJMQjlRpkJFZA0ZAl2yYPU2s7D03L76VZAblRkfO39EsZA6PbfnZCD7dD4gL8ZCrda3961D5ZByT8kFBNsV0Ado2vbtcK9ilKN3

## Step 1. Get a user token in [Graph API Explorer Tool](https://developers.facebook.com/tools/explorer)

USER_ACCESS_TOKEN

## Step 2. Get a PAGE_ACCESS_TOKEN and page id (Use the USER_ACCESS_TOKEN)

GET "https://graph.facebook.com/v24.0/me/accounts?access_token={USER_ACCESS_TOKEN}"

```
{
  "data": [
    {
      "access_token": "EAAQfIUidhhwBPiZBk....",
      "category": "Software",
      "category_list": [
        {
          "id": "2211",
          "name": "Software"
        }
      ],
      "name": "Test page",
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

## Step 3. Get page feed and select a post id (Use the page id and PAGE_ACCESS_TOKEN from step 2)

GET "https://graph.facebook.com/v24.0/{page_id}/feed?access_token={PAGE_ACCESS_TOKEN}"

```
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

## Step 4. Get post data (Use post id and PAGE_ACCESS_TOKEN)

### List each field you want. You can include as many as you need, separated by commas.

GET "https://graph.facebook.com/v24.0/{post_id}?fields=id,message,created_time,permalink_url,attachments,likes.summary(true),comments.summary(true),shares&access_token={PAGE_ACCESS_TOKEN}"

```
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
                        "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/55.846_1221028....._6636302388....._n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeGpfK-U0jpkVEZ2woEnrMXNkGssDve6EBiQaywO97oQGDwsvi-EytgwhDFVlbDfH-43bBU23guukyjOYRKRUiOy&_nc_ohc=NnN4AEcaXU8Q7kNvwGsMmLk&_nc_oc=AdkOH4vgDJ_H0bUucBJTRyTPldQ6Mfm5RWKIbrra_jXnvi1IPANAbuyYPZ_plTVjFjk&_nc_zt=23&_nc_ht=scontent.fcgm1-1.fna&edm=AJfPMC4EAAAA&_nc_gid=f1BREYMgHKdgRTNNFfV5HA&oh=00_AfdRbeqPxe6Ka0VPSfCDpfXd-AmdqG_sS3BfrLzpzG201A&oe=68EDC14E",
                        "width": 717
                    }
                },
                "subattachments": {
                    "data": [
                        {
                            "media": {
                                "image": {
                                    "height": 552,
                                    "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/550012846_122102805...._66363023882......_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeGpfK-U0jpkVEZ2woEnrMXNkGssDve6EBiQaywO97oQGDwsvi-EytgwhDFVlbDfH-43bBU23guukyjOYRKRUiOy&_nc_ohc=NnN4AEcaXU8Q7kNvwGsMmLk&_nc_oc=AdkOH4vgDJ_H0bUucBJTRyTPldQ6Mfm5RWKIbrra_jXnvi1IPANAbuyYPZ_plTVjFjk&_nc_zt=23&_nc_ht=scontent.fcgm1-1.fna&edm=AJfPMC4EAAAA&_nc_gid=f1BREYMgHKdgRTNNFfV5HA&oh=00_AfdRbeqPxe6Ka0VPSfCDpfXd-AmdqG_sS3BfrLzpzG201A&oe=68EDC14E",
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
                                    "src": "https://scontent.fcgm1-1.fna.fbcdn.net/v/t39.30808-6/549523301_1221028052.....1_3005173....._n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeHLaWeOAzstww_5lUk3bj0PidQbkzm0bVaJ1BuTObRtVizyrQM3fHVxWc6jVKL922cntz1vrNcIodHccvfUMzww&_nc_ohc=ObSRMdYJyIgQ7kNvwE8G5ib&_nc_oc=AdmOMconSzaWasHzA4R0dob-STxeGJ-2XIynjinHEI2Jos6i00IbunUcZM9cNR6sl0w&_nc_zt=23&_nc_ht=scontent.fcgm1-1.fna&edm=AJfPMC4EAAAA&_nc_gid=f1BREYMgHKdgRTNNFfV5HA&oh=00_Afezvuzo1kQY9Vt9yzDTk_A7Qih6pypi7jvHkkpZrGtWUw&oe=68EDC692",
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
                "title": "Photos from Test page's post",
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
