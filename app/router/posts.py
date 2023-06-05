from fastapi import APIRouter, Depends, status, HTTPException
from init_db import get_db
from schema import PostModel, PostUpdateModel, CommentModel, PostCreateModel
from typing import Annotated, List
from sqlalchemy.orm import Session
from models import User, Post, Comment
from authentication.jwt import get_current_active_user

router = APIRouter(
    prefix='/api/post',
    tags=['posts']
)

@router.post('/', status_code=status.HTTP_201_CREATED,response_model=PostModel)
async def create_post(post_model: PostCreateModel,user:Annotated[User, Depends(get_current_active_user)], db:Session = Depends(get_db)):
    # only staff user can create post
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not allowed to create post '
        )
    # check about slug
    slug = post_model.title.lower().replace(" ", "-")  # Generate slug from title
    if db.query(Post).filter(Post.slug == slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='the post we create with title is already have, change title'
        )
    
    post = Post(**post_model.dict(), slug=slug, user=user)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# Getting all post in blog
@router.get("/", response_model=List[PostModel])
def get_all_posts(db:Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts



# Getting all post in blog
@router.get("/{post_slug}", response_model=PostModel)
def get_post(post_slug:str, db:Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == post_slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post Not Founded'
        )
    return post

@router.put('/update/{blog_slug}', response_model=PostModel)
async def update_post(blog_slug:str, request:PostUpdateModel, user:Annotated[User, Depends(get_current_active_user)], db:Session = Depends(get_db)):
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not allowed to Update post '
        )
    # check about slug
    post =  db.query(Post).filter(Post.slug == blog_slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post Not Founded'
        )
    if request.title:
        post.title = request.title
        
    if request.description:
        post.description = request.description
        
    db.commit()
    db.refresh(post)
    return post    


@router.delete('/delete/{blog_slug}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(blog_slug:str, user:Annotated[User, Depends(get_current_active_user)], db:Session = Depends(get_db)):
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not allowed to delete post '
        )
    # check about slug
    post =  db.query(Post).filter(Post.slug == blog_slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post Not Founded'
        )
    db.delete(post)
    db.commit()
    return {'detail': 'Successfully Delete Post'}    

# Working With Comment

@router.post('/{blog_slug}/comment', response_model=PostModel)
async def delete_post(blog_slug:str,request:CommentModel, user:Annotated[User, Depends(get_current_active_user)], db:Session = Depends(get_db)):
    # get post
    post =  db.query(Post).filter(Post.slug == blog_slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post Not Founded'
        )
    
    comment = Comment(
        post_id=post.id,
        user_id=user.id,
        content=request.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return post

@router.delete("/comments/{comment_id}/update", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int,user:Annotated[User, Depends(get_current_active_user)],db:Session = Depends(get_db)):

    # Check if the comment exists
    comment: Comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=400, detail="You not allowed to delete comment")
    
    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}


@router.put("/comments/{comment_id}/update", status_code=status.HTTP_204_NO_CONTENT, response_model=CommentModel)
def delete_comment(comment_id: int, request:CommentModel, user:Annotated[User, Depends(get_current_active_user)],db:Session = Depends(get_db)):

    # Check if the comment exists
    comment: Comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=400, detail="You not allowed to delete comment")
    
    if request.content:
        comment.content = request.content 
   
    db.commit()
    db.refresh(comment)
    return comment