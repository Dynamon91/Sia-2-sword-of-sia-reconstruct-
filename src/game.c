#include "game.h"
#include "alignment.h"
/* Approximate first viewport from the supplied recording, not a recovered ROM map. */
const Platform platforms[PLATFORM_COUNT]={{81,88,70,8},{186,40,54,8}};
static const Platform bridge_platforms[3]={{33,BRIDGE_SURFACE_Y,48,8},{81,BRIDGE_SURFACE_Y,125,8},{206,BRIDGE_SURFACE_Y,34,8}};
static const Platform cliff_platforms[2]={{0,54,43,8},{96,115,144,8}};
static const Platform cliff_rock={96,115,144,45};
static const Platform lever_wall={0,-80,44,240};
static const Platform island_upper_ledge={0,60,56,8};
static const Platform gap_platforms[2]={{0,106,98,54},{172,98,68,62}};
/* Provisional walk planes for the registered 159s viewport. */
static const Platform continuation_solids[2]={{0,101,134,59},{202,95,12,65}};
static const int continuation_ground[][2]={{0,123},{48,123},{64,113},{80,105},{104,101},{133,101}};
int game_continuation_floor(int player_x){
 if(player_x<134&&player_x+PLAYER_W>0){
  int x=player_x+PLAYER_W/2;if(x<0)x=0;if(x>133)x=133;
  for(unsigned i=1;i<sizeof(continuation_ground)/sizeof(continuation_ground[0]);i++){
   if(x<=continuation_ground[i][0]){
    int x0=continuation_ground[i-1][0],y0=continuation_ground[i-1][1];
    return y0+(continuation_ground[i][1]-y0)*(x-x0)/(continuation_ground[i][0]-x0);
   }
  }
 }
 if(player_x+PLAYER_W>202&&player_x<240)return 95;
 return 4096;
}
static const Platform bridge_run_solids[2]={{32,104,12,56},{177,112,63,48}};
static const Platform upper_solids[2]={{22,100,56,18},{168,-80,72,240}};
static const int upper_ground[][2]={{0,72},{28,100},{77,100}};
static const Platform riser_solids[2]={{9,119,124,41},{133,-80,107,240}};
static const int bridge_run_ground[][2]={{177,112},{190,112},{206,108},{222,97},{239,92}};
/* The first five points are the preceding island translated by (-168,+7). */
static const int riser_ground[][2]={{9,119},{22,119},{38,115},{54,104},{71,99},{132,99}};
static int profile_height(const int points[][2],unsigned count,int x){
 for(unsigned i=1;i<count;i++)if(x<=points[i][0]){
  int x0=points[i-1][0],y0=points[i-1][1];
  return y0+(points[i][1]-y0)*(x-x0)/(points[i][0]-x0);
 }
 return points[count-1][1];
}
int game_extension_floor(int area,int player_x){
 if(area==5)return game_continuation_floor(player_x);
 int center=player_x+PLAYER_W/2,floor=4096;
 if(area==12)return player_x+PLAYER_W>0&&player_x<174?63:4096;
 if(area==13)return player_x+PLAYER_W>44&&player_x<220?149:4096;
 if(area==11){
  if((player_x+PLAYER_W>0&&player_x<84)||(player_x+PLAYER_W>140&&player_x<192))return 144;
  return 4096;
 }
 if(area==9&&player_x+PLAYER_W>0&&player_x<136){
  int x=center;if(x<0)x=0;if(x>135)x=135;
  return x<86?x-1:85;
 }
 if(area==10&&player_x+PLAYER_W>64&&player_x<200){
  int x=center;if(x<64)x=64;
  return x<116?100:x-16;
 }
 if(area==6){
  if(player_x+PLAYER_W>32&&player_x<177)floor=104;
  if(player_x+PLAYER_W>177&&player_x<240){
   int x=center;if(x<177)x=177;if(x>239)x=239;
   int surface=profile_height(bridge_run_ground,5,x);if(surface<floor)floor=surface;
  }
 }else if(area==7){
  if(player_x+PLAYER_W>0&&player_x<9)floor=111;
  if(player_x+PLAYER_W>9&&player_x<133){
   int x=center;if(x<9)x=9;if(x>132)x=132;
   int surface=profile_height(riser_ground,6,x);if(surface<floor)floor=surface;
  }
 }else if(area==8&&player_x+PLAYER_W>0&&player_x<78){
  int x=center;if(x<0)x=0;if(x>77)x=77;floor=profile_height(upper_ground,3,x);
 }
 return floor;
}
const Gem level_gems[GEM_COUNT]={{0,109,62,0},{1,133,74,1},{3,151,47,2},{4,126,40,3},{8,106,56,4}};
/* Animation and damage share the same attack clock: wind-up, contact, recovery. */
unsigned game_attack_frame(const Game *g){return g->attack>8?0:g->attack>=4?1:2;}
unsigned game_walk_frame(const Game *g){return g->walk_ticks/(6u*320u);}
unsigned game_air_frame(const Game *g){
 if(g->grounded||g->climbing||g->game_over)return AIR_NONE;
 /* Estimated near-apex window. Positive velocity always means falling,
    including walking off a platform or letting go of a ledge. */
 return g->vy < -FP/2 ? AIR_RISE : g->vy <= 0 ? AIR_APEX : AIR_FALL;
}
unsigned game_ledge_frame(const Game *g){
 if(g->climbing!=LEDGE_PULL)return 0;
 unsigned frame=1+g->ledge_ticks/4;
 return frame>3?3:frame;
}
static const int guard_ground[][2]={{0,130},{24,130},{48,120},{72,115},{96,102},{120,94},{144,88},{239,88}};
static const int ground[][2]={{0,151},{24,153},{40,158},{56,158},{72,153},{84,153},
 {100,154},{120,153},{140,145},{156,146},{176,153},{192,157},{216,157},{239,153}};
int game_floor(int x){
 if(x<0)x=0;
 if(x>239)x=239;
 for(unsigned i=1;i<sizeof(ground)/sizeof(ground[0]);i++)if(x<=ground[i][0]){
  int x0=ground[i-1][0],y0=ground[i-1][1];
  return y0+(ground[i][1]-y0)*(x-x0)/(ground[i][0]-x0);
 }
 return 153;
}
static int guard_floor(int x){
 for(unsigned i=1;i<sizeof(guard_ground)/sizeof(guard_ground[0]);i++)if(x<=guard_ground[i][0]){
 int x0=guard_ground[i-1][0],y0=guard_ground[i-1][1];return y0+(guard_ground[i][1]-y0)*(x-x0)/(guard_ground[i][0]-x0);}
 return 88;
}
void game_reset(Game *g){
 level_progress_reset(&g->progress,3);
 g->enemy4_x=80*FP;g->enemy4_dir=-1;g->enemy4_hp=2;g->enemy4_flash=0;g->enemy4_last_swing=0;
 g->enemy3_x=118*FP;g->enemy3_dir=-1;g->enemy3_hp=2;g->enemy3_flash=0;g->enemy3_last_swing=0;
 g->hurt_timer=0;g->game_over=0;g->walk_ticks=0;g->lives=3;
 g->enemy2_x=210*FP;g->enemy2_dir=-1;g->enemy2_hp=2;g->enemy2_flash=0;g->enemy2_last_swing=0;
 g->enemy_x=155*FP;g->enemy_dir=-1;g->enemy_hp=2;g->enemy_flash=0;g->swing_id=0;g->enemy_last_swing=0;
 level_set_checkpoint(&g->progress,0,40*FP,118*FP);
 g->x=40*FP;g->y=118*FP;g->vx=0;g->vy=0;
 g->grounded=1;g->facing=1;g->attack=0;g->camera=0;g->previous=0;
 g->climbing=0;g->gems=0;g->collected=0;g->sign_open=0;g->camera_y=0;
 g->ledge_y=0;g->ledge_ticks=0;g->ledge_cooldown=0;
 g->area=0;g->falls=0;g->pickup_timer=0;g->ticks=0;
}
static void camera(Game *g);
static void transition_area(Game *g,int area){
 int delta=area-g->area;
 g->x-=delta*AREA_OFFSET_X*FP;
 g->y+=delta*AREA_OFFSET_Y*FP;
 g->area=area;g->progress.area=(unsigned)area;g->climbing=0;g->sign_open=0;g->camera=0;
 camera(g);
}
static void respawn_area(Game *g){
 g->x=(g->area==4?60:g->area==3?10:g->area==2?20:g->area?60:40)*FP;g->y=(g->area==4?66:g->area==3?90:g->area==2?14:g->area?BRIDGE_SURFACE_Y-PLAYER_H:118)*FP;
 if(g->area==5){g->x=40*FP;g->y=(game_continuation_floor(40)-PLAYER_H)*FP;}
 if(g->area==6){g->x=60*FP;g->y=(game_extension_floor(6,60)-PLAYER_H)*FP;}
 if(g->area==7){g->x=60*FP;g->y=(game_extension_floor(7,60)-PLAYER_H)*FP;}
 if(g->area==8){g->x=50*FP;g->y=(game_extension_floor(8,50)-PLAYER_H)*FP;}
 if(g->area==9){g->x=65*FP;g->y=(game_extension_floor(9,65)-PLAYER_H)*FP;}
 if(g->area==10){g->x=85*FP;g->y=(game_extension_floor(10,85)-PLAYER_H)*FP;}
 if(g->area==11){g->x=154*FP;g->y=104*FP;}
 if(g->area==12){g->x=142*FP;g->y=23*FP;}
 if(g->area==13){g->x=174*FP;g->y=109*FP;}
 g->vx=0;g->vy=0;g->grounded=1;g->climbing=0;g->sign_open=0;
 g->camera=0;camera(g);
}
/* A fall or lethal hit consumes one life; run progress survives respawn. */
static void lose_life(Game *g){
 if(g->game_over)return;
 if(g->lives)g->lives--;
 /* Pickup feedback belongs to the lost life, while the collected gem survives. */
 g->pickup_timer=0;
 g->attack=0;g->walk_ticks=0;g->vx=0;g->vy=0;g->climbing=0;g->ledge_ticks=0;g->ledge_cooldown=0;
 if(!g->lives){g->progress.health=0;g->game_over=1;return;}
 g->progress.health=g->progress.max_health;
 respawn_area(g);g->hurt_timer=90;
}
static void camera(Game *g){
 if(g->area>=2){g->camera_y=0;return;}
 g->camera_y=g->y/FP-48;
 if(g->camera_y>0)g->camera_y=0;
 if(g->camera_y<-40)g->camera_y=-40;
}
static void collect(Game *g){
 for(unsigned i=0;i<GEM_COUNT;i++){
  const Gem *item=&level_gems[i];
  if(item->area!=g->area)continue;
  unsigned bit=1u<<item->id;
  if(!((unsigned)g->collected&bit)&&g->x+PLAYER_W*FP>item->x*FP&&g->x<(item->x+16)*FP&&
     g->y<(item->y+16)*FP&&g->y+PLAYER_H*FP>item->y*FP&&level_collect_gem(&g->progress,item->id)){
   g->collected|=(int)bit;g->gems=(int)g->progress.gems;g->pickup_timer=150;
  }
 }
}
int game_damage(Game *g,unsigned amount){
 if(g->game_over||g->hurt_timer||!amount)return 0;
 if(!level_take_damage(&g->progress,amount))return 0;
 g->climbing=0;g->ledge_ticks=0;g->ledge_cooldown=18;g->attack=0;g->hurt_timer=60;
 if(!g->progress.health)lose_life(g);
 return 1;
}
static void guard_step(Game *g){
 if((g->area<3||g->area>7)&&g->area!=12&&g->area!=13)return;
 int kind=g->area>=12?3:g->area>=6?2:g->area>=4?1:0;
 int second=kind==1;
 int *hp=kind==3?&g->enemy4_hp:kind==2?&g->enemy3_hp:second?&g->enemy2_hp:&g->enemy_hp;
 int *position=kind==3?&g->enemy4_x:kind==2?&g->enemy3_x:second?&g->enemy2_x:&g->enemy_x;
 int *direction=kind==3?&g->enemy4_dir:kind==2?&g->enemy3_dir:second?&g->enemy2_dir:&g->enemy_dir;
 int *flash=kind==3?&g->enemy4_flash:kind==2?&g->enemy3_flash:second?&g->enemy2_flash:&g->enemy_flash;
 unsigned *last=kind==3?&g->enemy4_last_swing:kind==2?&g->enemy3_last_swing:second?&g->enemy2_last_swing:&g->enemy_last_swing;
 if(!*hp)return;
 if(*flash>0)--*flash;
 *position+=*direction*64;
 int left=kind==3?65:kind==2?85:second?188:140,right=kind==3?100:kind==2?145:second?218:210;
 if(*position<left*FP){*position=left*FP;*direction=1;}
 if(*position>right*FP){*position=right*FP;*direction=-1;}
 int ex=*position/FP+(g->area==13?44:0)-(g->area==7?168:g->area==5?188:0);
 int ey=(kind==3?63+(g->area==13?86:0):kind==2?104+(g->area==7?7:0):second?98+(g->area==5?25:0):guard_floor(ex+7))-40;
 int px=g->x/FP,py=g->y/FP;
 int vertical=py+PLAYER_H>ey&&py<ey+40;
 int sword_left=g->facing>0?px+PLAYER_W:px-30;
 if(g->attack&&game_attack_frame(g)==1&&*last!=g->swing_id&&vertical&&sword_left+30>ex&&sword_left<ex+18){
  *last=g->swing_id;--*hp;*flash=12;
  if(!*hp){level_defeat_enemy(&g->progress,(unsigned)kind);return;}
 }
 if(vertical&&px+PLAYER_W>ex&&px<ex+18)game_damage(g,1);
}
void game_step(Game *g,unsigned input){
 if(input&RESET){
  game_reset(g);
  /* A held action belongs to the old run. Require release before retriggering. */
  g->previous=(int)(input&~RESET);return;
 }
 if(g->game_over)return;
 if(g->hurt_timer>0)g->hurt_timer--;
 unsigned pressed=input&~(unsigned)g->previous;g->previous=(int)input;g->ticks++;level_progress_tick(&g->progress,0);
 if(g->pickup_timer>0)g->pickup_timer--;
 if(g->ledge_cooldown)g->ledge_cooldown--;
 if(g->climbing){
  g->attack=0;g->vx=0;g->vy=0;g->walk_ticks=0;g->grounded=0;
  if(g->climbing==LEDGE_HANG){
   if(input&(DOWN|LEFT|RIGHT)){
    g->climbing=LEDGE_NONE;g->ledge_cooldown=18;g->vy=FP;
   }else if((input&UP)||(pressed&JUMP)){
    g->climbing=LEDGE_PULL;g->ledge_ticks=0;
   }
  }else{
   g->ledge_ticks++;
   g->y=(g->ledge_y+10)*FP-(int)g->ledge_ticks*(PLAYER_H+10)*FP/LEDGE_PULL_TICKS;
   if(g->ledge_ticks>=LEDGE_PULL_TICKS){
    g->y=(g->ledge_y-PLAYER_H)*FP;g->climbing=LEDGE_NONE;g->grounded=1;
   }
  }
  if(g->climbing||g->grounded){collect(g);camera(g);return;}
 }
 if((pressed&ATTACK)&&!g->attack){g->attack=12;g->swing_id++;}
 else if(g->attack)--g->attack;
 int old_floor=(g->area>=5?game_extension_floor(g->area,g->x/FP):g->area==3?guard_floor(g->x/FP+PLAYER_W/2):g->area?4096:game_floor(g->x/FP+PLAYER_W/2))*FP;
 int was_floor=g->grounded&&g->y+PLAYER_H*FP==old_floor;
 g->vx=((input&RIGHT)!=0)*320-((input&LEFT)!=0)*320;
 if(g->vx&&!g->attack)g->facing=g->vx>0?1:-1;
 int old_x=g->x;
 g->x+=g->vx;
 /* Solid rock volumes: resolve crossed faces without snapping onto the top. */
 const Platform *solids=g->area==13?&lever_wall:g->area==8?upper_solids:g->area==7?riser_solids:g->area==6?bridge_run_solids:g->area==5?continuation_solids:g->area==2?&cliff_rock:gap_platforms;
 int solid_count=(g->area==2||g->area==13)?1:g->area>=9?0:g->area>=4?2:0;
 for(int i=0;i<solid_count;i++){
  const Platform *p=&solids[i];
  if(g->y+PLAYER_H*FP<=p->y*FP||g->y>=(p->y+p->h)*FP)continue;
  if(g->vx>0&&old_x+PLAYER_W*FP<=p->x*FP&&g->x+PLAYER_W*FP>p->x*FP){
   g->x=(p->x-PLAYER_W)*FP;g->vx=0;
  }else if(g->vx<0&&old_x>=(p->x+p->w)*FP&&g->x<(p->x+p->w)*FP){
   g->x=(p->x+p->w)*FP;g->vx=0;
  }
 }
 if(g->x<0)g->x=0;
 if(g->x>(WORLD_W-PLAYER_W)*FP)g->x=(WORLD_W-PLAYER_W)*FP;
 /* Drive running from actual movement after collision, not held input. */
 int moved_x=g->x-old_x;
 if(!moved_x)g->vx=0;
 int center=g->x/FP+PLAYER_W/2;
 if((pressed&JUMP)&&g->grounded){g->vy=(g->area>=7&&(input&UP))?-1280:-960;g->grounded=0;}
 int old_bottom=g->y+PLAYER_H*FP;
 g->vy+=32;if(g->vy>6*FP)g->vy=6*FP;
 int next=g->y+g->vy,landing=0x7fffffff;
 /* Rising into a rock underside stops vertical motion, without grounding. */
 if(g->vy<0)for(int i=0;i<solid_count;i++){
  const Platform *p=&solids[i];int underside=(p->y+p->h)*FP;
  if(g->x+PLAYER_W*FP>p->x*FP&&g->x<(p->x+p->w)*FP&&
     g->y>=underside&&next<underside){next=underside;g->vy=0;}
 }
 g->grounded=0;
 const Platform *list=g->area==11?&island_upper_ledge:g->area==4?gap_platforms:g->area==2?cliff_platforms:g->area?bridge_platforms:platforms;
 int count=g->area==11?1:g->area>=5?0:g->area==4?2:g->area==3?0:g->area==2?2:g->area?3:PLATFORM_COUNT;
 for(int i=0;i<count;i++){
  const Platform *p=&list[i];
  if(g->vy>=0&&g->x+PLAYER_W*FP>p->x*FP&&g->x<(p->x+p->w)*FP&&
     old_bottom<=p->y*FP&&next+PLAYER_H*FP>=p->y*FP&&p->y*FP<landing)
   landing=p->y*FP;
 }
 int floor=(g->area>=5?game_extension_floor(g->area,g->x/FP):g->area==3?guard_floor(center):g->area?4096:game_floor(center))*FP;
 if(g->area>=5){
  /* Follow the authored slope while grounded; never snap up through rock. */
  if(floor<4096*FP&&g->vy>=0&&((was_floor)||(old_bottom<=floor&&next+PLAYER_H*FP>=floor))&&floor<landing)landing=floor;
 }else if((next+PLAYER_H*FP>=floor||(was_floor&&g->vy>=0))&&floor<landing)landing=floor;
 if(landing!=0x7fffffff){next=landing-PLAYER_H*FP;g->vy=0;g->grounded=1;}
 /* The reference shows a catch from a descending jump, then a pull-up.
    Only the two measured first-room ledges have authored catch geometry. */
 if(!g->area&&!g->grounded&&!g->ledge_cooldown&&g->vy>0&&!(input&DOWN)){
  for(int i=0;i<PLATFORM_COUNT;i++){
   const Platform *p=&platforms[i];int hang_y=(p->y+10)*FP;
   if(center>=p->x+12&&center<=p->x+p->w-12&&
      g->y<=hang_y&&next>=hang_y&&old_bottom>p->y*FP){
    next=hang_y;g->ledge_y=p->y;g->ledge_ticks=0;g->climbing=LEDGE_HANG;
    g->vx=0;g->vy=0;g->attack=0;g->walk_ticks=0;break;
   }
  }
 }
 g->y=next;g->camera=0;collect(g);camera(g);
 if(g->grounded&&moved_x&&!g->attack)
  g->walk_ticks=(g->walk_ticks+(unsigned)(moved_x<0?-moved_x:moved_x))%(18u*320u);
 else g->walk_ticks=0;
 if(!g->area&&(pressed&DOWN)&&center>=158&&center<=190&&g->grounded)g->sign_open=1;
 if(!g->area&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded&&g->y==0)transition_area(g,1);
 else if(g->area==1&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=32*FP&&g->grounded)transition_area(g,0);
 else if(g->area==1&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){g->area=2;g->progress.area=2;g->x=20*FP;g->y=14*FP;g->vy=0;camera(g);}
 else if(g->area==2&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=8*FP&&g->grounded){g->area=1;g->progress.area=1;g->x=224*FP;g->y=60*FP;g->vy=0;camera(g);}
 else if(g->area==2&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){g->area=3;g->progress.area=3;g->x=10*FP;g->y=90*FP;g->vy=0;camera(g);}
 else if(g->area==3&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=1*FP&&g->grounded){g->area=2;g->progress.area=2;g->x=224*FP;g->y=75*FP;g->vy=0;camera(g);}
 else if(g->area==3&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){
  g->area=4;g->progress.area=4;g->x-=158*FP;g->y+=18*FP;camera(g);
 }else if(g->area==4&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=32*FP&&g->grounded){
  g->area=3;g->progress.area=3;g->x+=158*FP;g->y-=18*FP;camera(g);
 }
 else if(g->area==4&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){
  g->area=5;g->progress.area=5;g->x-=188*FP;g->y+=25*FP;camera(g);
 }else if(g->area==5&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=32*FP&&g->grounded){
  g->area=4;g->progress.area=4;g->x+=188*FP;g->y-=25*FP;camera(g);
 }
 else if(g->area==5&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){
  g->area=6;g->progress.area=6;g->x-=170*FP;g->y+=9*FP;camera(g);
 }else if(g->area==6&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=32*FP&&g->grounded){
  g->area=5;g->progress.area=5;g->x+=170*FP;g->y-=9*FP;camera(g);
 }else if(g->area==6&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=225*FP&&g->grounded){
  g->area=7;g->progress.area=7;g->x-=168*FP;g->y+=7*FP;camera(g);
 }else if(g->area==7&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=32*FP&&g->grounded){
  g->area=6;g->progress.area=6;g->x+=168*FP;g->y-=7*FP;camera(g);
 }
 else if(g->area==8&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=12*FP&&g->grounded){
  g->area=9;g->progress.area=9;g->x+=58*FP;g->y-=15*FP;camera(g);
 }else if(g->area==9&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=75*FP&&g->grounded){
  g->area=8;g->progress.area=8;g->x-=58*FP;g->y+=15*FP;camera(g);
 }else if(g->area==9&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=42*FP&&g->grounded){
  g->area=10;g->progress.area=10;g->x+=108*FP;g->y+=93*FP;camera(g);
 }else if(g->area==10&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=151*FP&&g->grounded){
  g->area=9;g->progress.area=9;g->x-=108*FP;g->y-=93*FP;camera(g);
 }else if(g->area==10&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=78*FP&&g->grounded){
  g->area=11;g->progress.area=11;g->x+=76*FP;g->y+=44*FP;camera(g);
 }else if(g->area==11&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=160*FP&&g->grounded){
  g->area=10;g->progress.area=10;g->x-=76*FP;g->y-=44*FP;camera(g);
 }else if(g->area==11&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=24*FP&&g->grounded&&g->y==20*FP){
  g->area=12;g->progress.area=12;g->x+=118*FP;g->y+=3*FP;camera(g);
 }else if(g->area==12&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=150*FP&&g->grounded){
  g->area=11;g->progress.area=11;g->x-=118*FP;g->y-=3*FP;camera(g);
 }else if(g->area==12&&((input&(LEFT|RIGHT))==LEFT)&&g->x<=130*FP&&g->grounded){
  g->area=13;g->progress.area=13;g->x+=44*FP;g->y+=86*FP;camera(g);
 }else if(g->area==13&&((input&(LEFT|RIGHT))==RIGHT)&&g->x>=176*FP&&g->grounded){
  g->area=12;g->progress.area=12;g->x-=44*FP;g->y-=86*FP;camera(g);
 }else if(g->area==7&&g->x<90*FP&&g->y<=-8*FP&&g->vy<0){
  g->area=8;g->progress.area=8;g->x+=35*FP;g->y+=81*FP;camera(g);
 }else if(g->area==8&&g->y>=110*FP&&!g->grounded){
  g->area=7;g->progress.area=7;g->x-=35*FP;g->y-=81*FP;
  if(g->x<0)g->x=0;
  camera(g);
 }
 else if(g->y>210*FP){g->falls++;lose_life(g);return;}
 guard_step(g);
}
